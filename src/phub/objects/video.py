from __future__ import annotations
import html
import os
import random
import logging
from functools import cached_property
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterator, Literal, Callable, Any
from . import Tag, Like, User, Image
from .. import utils
from .. import errors
from .. import consts
from .. import literals
from ..modules import download, parser, display
if TYPE_CHECKING:
    from ..core import Client
    from ..utils import Quality
logger = logging.getLogger(__name__)


class Video:
    """
    Represents a Pornhub video.
    """

    def __init__(self, client, url):
        """
        Initialise a new video object.

        Args:
            client (Client): The parent client.
            url       (str): The video URL.
        """
        if not consts.re.is_video_url(url):
            raise errors.URLError('Invalid video URL:', url)
        self.client = client
        self.url = url
        self.key = consts.re.get_viewkey(url)
        self.page: str = None
        self.data: dict = {}
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        self.ALLOW_QUERY_SIMULATION = False
        logger.debug('Initialised new video object %s', self)

    def __repr__(self):
        return f'phub.Video(key={self.key})'

    def refresh(self, page=True, data=True):
        """
        Refresh video data.

        Args:
            page (bool): Whether to refresh the video page.
            data (bool): Whether to refresh the video data.
        """
        logger.info('Refreshing %s cache', self)
        if page:
            self.page = None
        if data:
            self.data.clear()
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                logger.debug('Deleting key %s', key)
                delattr(self, key)

    def fetch(self, key):
        """
        Lazily fetch some data.

        key format:
            data@<dkey>   => Get key from API 
            page@<pkey>   => Scrape key from page
            <dkey>|<pkey> => Choose considering cache

        Args:
            key (str): The key to fetch.

        Returns:
            Any: The fetched or cached object.

        """
        if '|' in key:
            datakey, pagekey = key.split('|')
            if self.page:
                key = 'page@' + pagekey
            key = 'data@' + datakey
        if key in self.data:
            return self.data.get(key)
        logger.debug('Fetching %s key %s', self, key)
        if key.startswith('data@'):
            url = utils.concat(consts.API_ROOT, 'video_by_id?id=' + self.key)
            data = self.client.call(url).json()
            if 'message' in data:
                logger.warning(
                    'Video %s is not available. Error code: %s', self, data.get('code'))
                raise errors.VideoError(
                    f"Video is not available. Reason: {data['message']}")
            self.data |= {f'data@{k}': v for k, v in data['video'].items()}
        elif key.startswith('page@'):
            self.page = self.client.call(self.url).text
            data = parser.resolve(self)
            self.data |= {f'page@{k}': v for k, v in data.items()}
        return self.data.get(key)

    def dictify(self, keys='all', recursive=False):
        """
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: A dict version of the object.
        """
        return utils.dictify(self, keys, ['url', 'key', 'title', 'image', 'is_vertical', 'duration', 'tags', 'like', 'views', 'hotspots', 'date', 'pornstars', 'categories', 'orientation', 'author'], recursive)

    def get_M3U_URL(self, quality):
        """
        The URL of the master M3U file.

        Args:
            quality (Quality): The video quality.

        Returns:
            str: The M3U url.
        """
        from ..utils import Quality
        qualities = {int(q['quality']): q['videoUrl'] for q in self.fetch(
            'page@mediaDefinitions') if str(q['quality']).isdigit()}
        logger.info('Extracted %s qualities from %s', len(qualities), self)
        return Quality(quality).select(qualities)

    def get_segments(self, quality):
        """
        Get the video segment URLs.

        Args:
            quality (Quality): The video quality.

        Returns:
            Iterator: A segment URL iterator.
        """
        master_url = self.get_M3U_URL(quality)
        master_src = self.client.call(master_url).text
        urls = [l for l in master_src.split(
            '\n') if l and (not l.startswith('#'))]
        if len(urls) != 1:
            raise errors.ParsingError('Multiple index files found.')
        dns = master_url.split('master.m3u8')[0]
        url = urls[0]
        raw = self.client.call(dns + url).text
        for line in raw.split('\n'):
            if line.strip() and (not line.startswith('#')):
                yield (dns + line)

    def download(self, path, quality='best', *, downloader=download.default, display=display.default()):
        """
        Download the video to a file.

        Args:
            path (PathLike): The download path.
            quality (Quality | str | int): The video quality.
            downloader (Callable): The download backend.
            display (Callable): The progress display.

        Returns:
            str: The downloader video path.
        """
        if os.path.isdir(path):
            path = utils.concat(path, self.key + '.mp4')
        logger.info('Starting download for %s at %s', self, path)
        downloader(video=self, quality=quality, callback=display, path=path)
        return path

    def get_direct_url(self, quality):
        """
        Get the direct video URL given a specific quality.

        Args:
            quality (Quality): The video quality.

        Returns:
            str: The direct url.
        """
        from ..utils import Quality
        qual = Quality(quality)
        sources = self.fetch('page@mediaDefinitions')
        remote = [s for s in sources if 'remote' in s][0]['videoUrl']
        quals = {int(s['quality']): s['videoUrl']
                 for s in self.client.call(remote).json()}
        return qual.select(quals)

    def _assert_internal_success(self, res):
        """
        Assert an internal response has succeeded.

        Args:
            res (dict): The rerquest json response. 
        """
        if 'success' in res and (not res['success']):
            raise Exception(f"Call failed: `{res.get('message')}`")

    @cached_property
    def _as_query(self):
        """
        Simulate a query to gain access to more data.
        If the video object is yielded by a query, this property
        will be overriden by the query data.

        Warning - This will make a lot of requests and can fake
                   some properties (like watched).
        """
        if not self.ALLOW_QUERY_SIMULATION:
            from . import queries
            parent = self.data.get('query@parent')
            if isinstance(parent, queries.JSONQuery):
                raise Exception(
                    'Data is not available while using the hubtraffic wrapper. Please set use_hubtraffic=False in query initialisation.')
            raise Exception('Query simulation is disabled for this video object. If you still want to continue, set video.ALLOW_QUERY_SIMULATION=True. Be advised this method is not recomended and requires user logging.')
        logger.warning('Attempting query simulation')
        name = f'temp-{random.randint(0, 100)}'
        logger.info('Creating temporary playlist %s', name)
        res = self.client.call('playlist/create', 'POST', dict(title=name,
                               tags='["porn"]', description='', status='private', token=self.client._granted_token)).json()
        self._assert_internal_success(res)
        playlist_id = res.get('id')
        res = self.client.call('playlist/video_add', 'POST', dict(
            pid=playlist_id, vid=self.id, token=self.client._granted_token))
        self._assert_internal_success(res.json())
        from .query import queries
        query = queries.VideoQuery(self.client, f'playlist/{playlist_id}')
        raw = query._get_page(0)[0]
        keys = ('id', 'key', 'title', 'image', 'preview', 'markers')
        data = {k: v for k, v in zip(keys, consts.re.eval_video(raw))} | {
            'raw': raw}
        logger.info('Deleting playlist %s', name)
        res = self.client.call(
            'playlist/delete', 'POST', dict(pid=playlist_id, token=self._token, action='delete'))
        return data

    def like(self, toggle=True):
        """
        Set the video like value.

        Args:
            toggle (bool): The toggle value.
        """
        self.client.call('video/rate', 'POST', dict(id=self.id, current=self.likes.up,
                         value=int(toggle), token=self.client._granted_token))

    def favorite(self, toggle=True):
        """
        Set video as favorite or not.

        Args:
            toggle (bool): The toggle value.
        """
        res = self.client.call('video/favourite', 'POST', dict(
            toggle=int(toggle), id=self.id, token=self.client._granted_token))
        self._assert_internal_success(res.json())

    def watch_later(self, toggle=True):
        """
        Add or remove the video to the watch later playlist.

        Args:
            toggle (bool): The toggle value.
        """
        mod = 'add' if toggle else 'remove'
        res = self.client.call(f'playlist/video_{mod}_watchlater', 'POST', dict(
            vid=self.id, token=self.client._granted_token))
        self._assert_internal_success(res.json())

    @cached_property
    def id(self):
        """
        The internal video id.
        """
        if self.data.get('page@id'):
            return self.data.get('page@id')
        if self.data.get('page@playbackTracking'):
            return self.data.get('page@playbackTracking').get('video_id')
        return consts.re.get_thumb_id(self.image.url)

    @cached_property
    def title(self):
        """
        The video title.
        """
        return html.unescape(self.data.get('page@video_title') or self.fetch('data@title'))

    @cached_property
    def image(self):
        """
        The video thumbnail.
        """
        url = self.data.get('page@image_url')
        if url:
            servers = None
        else:
            url = self.fetch('data@thumb')
            servers = self.fetch('data@thumbs')
        return Image(client=self.client, url=url, servers=servers, name=f'thumb-{self.key}')

    @cached_property
    def is_vertical(self):
        """
        Whether the video is in vertical mode.
        """
        return bool(self.fetch('page@isVertical'))

    @cached_property
    def duration(self):
        """
        The video length.
        """
        if self.data.get('page@video_duration'):
            delta = {'seconds': self.data.get('page@video_duration')}
        else:
            params = ('seconds', 'minutes', 'hours', 'days')
            raw = self.fetch('data@duration')
            digits = list(map(int, raw.split(':')))[::-1]
            delta = {k: v for k, v in zip(params, digits)}
        return timedelta(**delta)

    @cached_property
    def tags(self):
        """
        The video tags.
        """
        return [Tag(tag['tag_name']) for tag in self.fetch('data@tags')]

    @cached_property
    def likes(self):
        """
        Positive and negative reviews of the video.
        """
        rating = self.fetch('data@rating') / 100
        counter = self.fetch('data@ratings')
        return Like(up=round(rating * counter), down=round((1 - rating) * counter), ratings=rating)

    @cached_property
    def views(self):
        """
        How many people watched the video.
        """
        return self.fetch('data@views')

    @cached_property
    def hotspots(self):
        """
        List of hotspots (in seconds) of the video.
        """
        return map(int, self.fetch('page@hotspots'))

    @cached_property
    def date(self):
        """
        The video publish date.
        """
        raw = self.fetch('data@publish_date')
        return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')

    @cached_property
    def pornstars(self):
        """
        The pornstars present in the video.
        """
        return [User.get(self.client, ps['pornstar_name']) for ps in self.fetch('data@pornstars')]

    @cached_property
    def categories(self):
        """
        The categories of the video.
        """
        return [item['category'] for item in self.fetch('data@categories')]

    @cached_property
    def orientation(self):
        """
        Video sexual orientation (e.g. straight).
        """
        return self.fetch('data@segment')

    @cached_property
    def author(self):
        """
        The video's author.
        """
        return User.from_video(self)

    @cached_property
    def is_free_premium(self):
        """
        Whether the video is part of free premium.
        """
        return 'phpFreeBlock' in self._as_query['markers']

    @cached_property
    def preview(self):
        """
        The preview 'mediabook' of the video.
        This is the lazy video displayed when hovering the video.
        """
        return Image(client=self.client, url=self._as_query['preview'], name=f'preview-{self.key}')

    @cached_property
    def is_HD(self):
        """
        Whether the video is in High Definition.
        """
        return self.fetch('page@isHD') == 'true'

    @cached_property
    def is_VR(self):
        """
        Whether the video is in Virtual Reality.
        """
        return self.fetch('page@isVR') == 'true'

    @cached_property
    def embed(self):
        """
        The video iframe embed.
        """
        return self.data.get('page@embedCode') or f'{consts.HOST}/embed/{self.id}'

    @property
    def liked(self):
        """
        Whether the video was liked by the account.
        """
        return NotImplemented

    @property
    def watched(self):
        """
        Whether the video was viewed previously by the account.
        """
        assert self.client.logged, 'Client must be logged in to use this property'
        if self.page:
            return True
        if 'watchedVideo' in self._as_query['markers']:
            return True
        if 'class="watchedVideoText' in self._as_query['raw']:
            return True
        return False

    @property
    def is_favorite(self):
        """
        Whether the video has been set as favorite by the client.
        """
        return bool(consts.re.is_favorite(self.page, False))
