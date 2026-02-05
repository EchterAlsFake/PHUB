from __future__ import annotations

import html
import os
import random
import logging
import traceback
from functools import cached_property

import httpx
from base_api.base import setup_logger
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterator, Literal, Callable, Any, Union

from httpx import request

from . import Tag, Like, User, Image
from .. import utils
from .. import errors
from .. import consts
from .. import literals
from ..modules import parser, display

if TYPE_CHECKING:
    from ..core import Client


class Video:
    '''
    Represents a Pornhub video.
    '''

    # === Base methods === #

    def __init__(self, client: Client, url: str, change_title_language: bool = False) -> None:
        '''
        Initialise a new video object.

        Args:
            client (Client): The parent client.
            url (str): The video URL.
        '''

        url = utils.fix_url(url)
        if not consts.re.is_video_url(url):
            raise errors.URLError('Invalid video URL:', url)

        self.logger = setup_logger(name="PHUB API - [Video]", log_file=None, level=logging.ERROR)
        self.client = client
        self.change_titles = change_title_language
        self.use_webmaster_api = self.client.use_webmaster_api
        self.url = url
        self.key = consts.re.get_viewkey(url)
        self.data: dict = {}  # The video webmasters data

        if self.use_webmaster_api is False:
            self.page = self.fetch("page@")

        else:
            self.page: str = None  # The video page content

        # Save data keys so far, so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']

        self.ALLOW_QUERY_SIMULATION = False

        self.logger.debug('Initialised new video object %s', self)
        self.logger.debug(f"Video data: {self.data}")

    def __repr__(self) -> str:

        return f'phub.Video(key={self.key})'

    def enable_logging(self, log_file: str = None, level=None, log_ip=None, log_port=None):
        self.logger = setup_logger(name="PHUB API - [Video]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    def refresh(self, page: bool = True, data: bool = True) -> None:
        '''
        Refresh video data.

        Args:
            page (bool): Whether to refresh the video page.
            data (bool): Whether to refresh the video data.
        '''

        self.logger.info('Refreshing %s cache', self)

        # Clear saved video page and data
        if page: self.page = None
        if data: self.data.clear()

        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                self.logger.debug('Deleting key %s', key)
                delattr(self, key)

    def fetch(self, key: str) -> Any:
        '''
        Lazily fetch some data.

        key format:
            data@<dkey>   => Get key from API
            page@<pkey>   => Scrape key from page
            <dkey>|<pkey> => Choose considering cache

        Args:
            key (str): The key to fetch.

        Returns:
            Any: The fetched or cached object.

        '''

        # Multiple keys handle
        if '|' in key:
            datakey, pagekey = key.split('|')

            if self.page and self.use_webmaster_api is False:
                key = 'page@' + pagekey

            else:
                key = 'data@' + datakey

        # If key is already cached
        if key in self.data:
            return self.data.get(key)

        self.logger.debug('Fetching %s key %s', self, key)

        # Fetch only webmasters data
        if key.startswith('data@'):
            url = utils.concat(consts.API_ROOT, 'video_by_id?id=' + self.key)
            data = self.client.call(url).json()

            if 'message' in data:
                self.logger.warning('Video %s is not available. Error code: %s', self, data.get('code'))

                if data.get('code') == "2002":
                    raise errors.RegionBlocked("The video is not available in your country.")

                else:
                    raise errors.VideoError(f'Video is not available. Reason: {data["message"]}')

            self.data |= {f'data@{k}': v for k, v in data['video'].items()}

        # Fetch raw page
        elif key.startswith('page@'):
            self.page = self.client.call(self.url).text
            data = parser.resolve(self)
            self.data |= {f'page@{k}': v for k, v in data.items()}

        return self.data.get(key)

    def dictify(self,
                keys: Literal['all'] | list[str] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: A dict version of the object.
        '''

        return utils.dictify(self, keys, [
            'url', 'key', 'title', 'image', 'is_vertical', 'duration',
            'tags', 'like', 'views', 'hotspots', 'date', 'pornstars',
            'categories', 'orientation', 'author'
        ], recursive)

    # === Download methods === #

    @cached_property
    def m3u8_base_url(self) -> str:
        """Builds a fake master.m3u8 playlist from quality-specific m3u8 URLs."""
        # I know that this is not a URL, but this will be handled specifically in eaf_base_api

        """
        Yo, if you are my future boss inspecting this code right now, and you search for the sense or logic here and why
        I did this, please immediately stop. Call an ambulance for yourself, because you will definitely get a brain
        damage, or just invite me directly into a call and I explain why I did it. 
        
        I am not responsible for any deaths, damages, or other losses caused by reading this code infrastructure lmao.
        """

        playlist_lines = ['#EXTM3U']
        for (width, height), uri in self.get_m3u8_urls.items():
            playlist_lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION={width}x{height}')
            playlist_lines.append(uri)
        return '\n'.join(playlist_lines)

    @cached_property
    def get_m3u8_urls(self) -> dict:
        '''
        The URL of the master M3U file.

        Args:
            quality (Quality): The video quality.

        Returns:
            str: The M3U url.
        '''

        raw_qualities = self.fetch('page@mediaDefinitions')
        quality_urls = {}

        for q in raw_qualities:
            if q.get('format') != 'hls' or not q.get('videoUrl'):
                continue

            try:
                width = int(q.get('width', 0))
                height = int(q.get('height', 0))
                url = q['videoUrl']
                quality_urls[(width, height)] = url

            except Exception as e:
                self.logger.warning(f"Skipping invalid quality entry: {q}, {e}")
                continue
        return quality_urls

    def get_segments(self, quality) -> list:
        """
        :param quality: (str) The video quality
        :return: (list) A list of segments (URLs)
        """
        segments = self.client.core.get_segments(m3u8_url_master=self.m3u8_base_url, quality=quality)
        return segments

    def download(self,
                 path: Union[str, os.PathLike],
                 downloader: Union[Callable, str] = "threaded",
                 quality: str = 'best',
                 remux: bool = False,
                 display_remux: Callable[[int, int], None] = None,
                 *,
                 display: Callable[[int, int], None] = display.default()) -> str:
        '''
        Download the video to a file.

        Args:
            path (PathLike): The download path.
            quality (Quality | str | int): The video quality.
            downloader (Callable): The download backend.
            display (Callable): The progress display.
            remux (bool): Whether to remux the video from MPEG-TS to MP4 (h264)
            display_remux (Callable[[int, int], None], optional): The display backend for remuxing.

        Returns:
            str: The downloader video path.
        '''

        # Add a name if the path is a directory
        if os.path.isdir(path):
            path = utils.concat(path, self.key + '.mp4')

        self.logger.info('Starting download for %s at %s', self, path)

        try:
            self.client.core.download(video=self, quality=quality, path=path, callback=display, downloader=downloader,
                                      remux=remux, callback_remux=display_remux)

        except Exception as e:
            error = traceback.format_exc()
            self.logger.error(f"An error occurred while downloading video {error}")

        return path

    # === Interaction methods === #

    def _assert_internal_success(self, res: dict) -> None:
        '''
        Assert an internal response has succeeded.

        Args:
            res (dict): The rerquest json response.
        '''

        if 'success' in res and not res['success']:
            raise Exception(f'Call failed: `{res.get("message")}`')

    @cached_property
    def _as_query(self) -> dict[str, str]:
        '''
        Simulate a query to gain access to more data.
        If the video object is yielded by a query, this property
        will be overriden by the query data.

        Warning - This will make a lot of requests and can fake
                   some properties (like watched).
        '''

        # Now I really don't want people to use this without knowing what it
        # really does
        if not self.ALLOW_QUERY_SIMULATION:

            # Personnalised error for the JSONQuery
            from . import queries
            parent = self.data.get('query@parent')

            if isinstance(parent, queries.JSONQuery): raise Exception(
                'Data is not available while using the hubtraffic wrapper. '
                'Please set use_hubtraffic=False in query initialisation.'
            )

            raise Exception(
                'Query simulation is disabled for this video object. '
                'If you still want to continue, set video.ALLOW_QUERY_SIMULATION=True. '
                'Be advised this method is not recommended and requires user logging.'
            )

        self.logger.warning('Attempting query simulation')

        # 1. Create playlist
        name = f'temp-{random.randint(0, 100)}'
        self.logger.info('Creating temporary playlist %s', name)
        res = self.client.call('playlist/create', 'POST', dict(
            title=name,
            tags='["porn"]',
            description='',
            status='private',
            token=self.client._granted_token
        )).json()

        self._assert_internal_success(res)
        playlist_id = res.get('id')

        # 2. Add to playlist
        res = self.client.call('playlist/video_add', 'POST', dict(
            pid=playlist_id,
            vid=self.id,
            token=self.client._granted_token
        ))

        self._assert_internal_success(res.json())

        # 3. Start query
        from .query import queries
        query = queries.VideoQuery(self.client, f'playlist/{playlist_id}')
        raw = query._get_page(0)[0]

        keys = ('id', 'key', 'title', 'image', 'preview', 'markers')
        data = {k: v for k, v in zip(keys, consts.re.eval_video(raw))} | {'raw': raw}

        # 4. Delete playlist
        self.logger.info('Deleting playlist %s', name)
        res = self.client.call('playlist/delete', 'POST', dict(
            pid=playlist_id,
            token=self._token,
            action='delete'
        ))

        return data

    def like(self, toggle: bool = True) -> None:
        '''
        Set the video like value.

        Args:
            toggle (bool): The toggle value.
        '''

        self.client.call('video/rate', 'POST', dict(
            id=self.id,
            current=self.likes.up,
            value=int(toggle),
            token=self.client._granted_token
        ))

    def favorite(self, toggle: bool = True) -> None:
        '''
        Set video as favorite or not.

        Args:
            toggle (bool): The toggle value.
        '''

        res = self.client.call('video/favourite', 'POST', dict(
            toggle=int(toggle),
            id=self.id,
            token=self.client._granted_token
        ))

        self._assert_internal_success(res.json())

    def watch_later(self, toggle: bool = True) -> bool:
        '''
        Add or remove the video to the watch later playlist.

        Args:
            toggle (bool): The toggle value.
        '''

        if toggle:
            res = self.client.call(f'api/v1/playlist/video_add_watchlater', 'POST', dict(
                vid=self.id,
                token=self.client._granted_token
            ))
            return res.is_success

        else:
            res = self.client.call(
                "api/v1/playlist/video_remove_watchlater",
                method="DELETE",
                params={"vid": str(self.id), "token": str(self.client._granted_token)},
                headers={"Accept": "application/json"},
            )
            return res.is_success


    # === Data properties === #

    @cached_property
    def id(self) -> str:
        '''
        The internal video id.
        '''

        if id_ := self.data.get('page@id'):
            return id_

        if pt := self.data.get('page@playbackTracking'):
            return pt.get('video_id')

        # Use thumbnail URL
        return consts.re.get_thumb_id(self.image.url)

    @cached_property
    def title(self) -> str:
        '''
        The video title.
        '''
        if self.change_titles:
            if not self.page:
                self.fetch("page@")

            return html.unescape(consts.re.fixed_title(self.page))

        else:
            return html.unescape(self.data.get('page@video_title')  # Use page title if cached
                                 or self.fetch('data@title'))  # Use HubTraffic by default

    @cached_property
    def image(self) -> Image:
        '''
        The video thumbnail.
        '''
        url = self.data.get('page@image_url') or self.data.get('data@thumb')
        if url:
            servers = None

        else:
            url = self.fetch('data@thumb')
            servers = self.data.get('data@thumbs') or []  # TODO - Use cache on prop Image.servers

        return Image(client=self.client,
                     url=url,
                     servers=servers,
                     name=f'thumb-{self.key}')

    @cached_property
    def is_vertical(self) -> bool:
        '''
        Whether the video is in vertical mode.
        '''

        return bool(self.fetch('page@isVertical'))

    @cached_property
    def duration(self) -> timedelta:
        '''
        The video length.
        '''

        if seconds := self.data.get('page@video_duration'):
            delta = {'seconds': seconds}

        else:
            params = ('seconds', 'minutes', 'hours', 'days')
            raw = self.fetch('data@duration')
            digits = list(map(int, raw.split(':')))[::-1]
            delta = {k: v for k, v in zip(params, digits)}

        return timedelta(**delta)

    @cached_property
    def tags(self) -> list[Tag]:
        '''
        The video tags.
        '''

        # TODO - Can be harvested on page
        return [Tag(tag['tag_name'])
                for tag in self.fetch('data@tags')]

    @cached_property
    def likes(self) -> Like:
        '''
        Positive and negative reviews of the video.
        '''

        # TODO - Can be harvested on page
        rating = self.fetch('data@rating') / 100
        counter = self.fetch('data@ratings')

        return Like(up=round(rating * counter),
                    down=round((1 - rating) * counter),
                    ratings=rating)

    @cached_property
    def views(self) -> int:
        '''
        How many people watched the video.
        '''

        # TODO - Can be harvested on page
        return self.fetch('data@views')

    @cached_property
    def hotspots(self) -> Iterator[int]:
        '''
        List of hotspots (in seconds) of the video.
        '''

        return map(int, self.fetch('page@hotspots'))

    @cached_property
    def date(self) -> datetime:
        '''
        The video publish date.
        '''

        raw = self.fetch('data@publish_date')
        return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')

    @cached_property
    def pornstars(self) -> list[User]:
        '''
        The pornstars present in the video.
        '''

        # TODO - Can be harvested on page and cache more data
        return [User.get(self.client, ps['pornstar_name'])
                for ps in self.fetch('data@pornstars')]

    @cached_property
    def categories(self) -> list[literals.category]:
        '''
        The categories of the video.
        '''

        return [item['category'] for item in self.fetch('data@categories')]

    @cached_property
    def orientation(self) -> str:
        '''
        Video sexual orientation (e.g. straight).
        '''

        return self.fetch('data@segment')

    @cached_property
    def author(self) -> User:
        '''
        The video's author.
        '''

        return User.from_video(self)

    @cached_property
    def is_free_premium(self) -> bool:
        '''
        Whether the video is part of free premium.
        '''

        return 'phpFreeBlock' in self._as_query['markers']

    @cached_property
    def preview(self) -> Image:
        '''
        The preview 'mediabook' of the video.
        This is the lazy video displayed when hovering the video.
        '''

        return Image(client=self.client,
                     url=self._as_query['preview'],
                     name=f'preview-{self.key}')

    @cached_property
    def is_HD(self) -> bool:
        '''
        Whether the video is in High Definition.
        '''

        return self.fetch('page@isHD') == 'true'

    @cached_property
    def is_VR(self) -> bool:
        '''
        Whether the video is in Virtual Reality.
        '''

        return self.fetch('page@isVR') == 'true'

    @cached_property
    def embed(self) -> str:
        '''
        The video iframe embed.
        '''

        return self.data.get('page@embedCode') or f'{consts.HOST}/embed/{self.id}'

    # === Dynamic data properties === #

    @property
    def liked(self) -> bool:
        '''
        Whether the video was liked by the account.
        '''

        return NotImplemented

    @property
    def watched(self) -> bool:
        '''
        Whether the video was viewed previously by the account.
        '''

        assert self.client.logged, 'Client must be logged in to use this property'

        # Use query sortcut if possible
        if self.data.get('query@watched'):
            return True

        # Search in markers
        if 'class="watchedVideoText' in self._as_query['raw']:
            return True

        # Evaluate on page (TODO)
        if self.page:
            ...

        return False

    @property
    def is_favorite(self) -> bool:
        '''
        Whether the video has been set as favorite by the client.
        '''

        return bool(consts.re.is_favorite(self.page, False))

# EOF
