from __future__ import annotations

import os
import random
import logging
from functools import cached_property
from datetime import datetime, timedelta
from typing import (TYPE_CHECKING, Iterator, Literal,
                    LiteralString, Callable, Any)

from . import Tag, Like, User, Image, Param
from .. import utils
from .. import errors
from .. import consts
from ..modules import download, parser, display

if TYPE_CHECKING:
    from ..core import Client
    from ..locals import Quality, Category

logger = logging.getLogger(__name__)


class Video:
    '''
    Represents a Pornhub video.
    '''
    
    # === Base methods === #
    
    def __init__(self, client: Client, url: str) -> None:
        '''
        Initialise a new video object.
        
        Args:
            client (Client): The parent client.
            url       (str): The video URL.
        '''
        
        if not consts.re.is_video_url(url):
            raise errors.URLError('Invalid video URL:', url)
        
        self.client = client
        
        self.url = url
        self.key = consts.re.get_viewkey(url)
        
        self.page: str = None # The video page content
        self.data: dict = {}  # The video webmasters data
        
        # Save data keys so far, so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        
        logger.debug('Initialised new video object %s', self)
    
    def __repr__(self) -> str:
        
        return f'phub.Video(key={self.key})'
        
    def refresh(self, page: bool = True, data: bool = True) -> None:
        '''
        Refresh video data.
        
        Args:
            page (bool): Whether to refresh the video page.
            data (bool): Whether to refresh the video data.
        '''
        
        logger.info('Refreshing %s cache', self)
        
        # Clear saved video page and data 
        if page: self.page = None
        if data: self.data.clear()
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                logger.debug('Deleting key %s', key)
                delattr(self, key)
     
    def fetch(self, key: str) -> Any:
        '''
        Lazily fetch some data.
        
        data@key => Use webmasters
        page@key => Use web scrapers
        
        Args:
            key (str): The key to fetch.
        
        Returns:
            Any: The fetched or cached object.
        
        '''
        
        if key in self.data:
            return self.data.get(key)
        
        logger.debug('Fetching %s key %s', self, key)
        
        # Fetch only webmasters data
        if key.startswith('data@'):
            
            url = utils.concat(consts.API_ROOT, 'video_by_id?id=' + self.key)
            data = self.client.call(url).json()
            
            if 'message' in data:
                logger.warning('Video %s is not available. Error code: %s', self, data.get('code'))
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
    
    def get_M3U_URL(self, quality: Quality) -> str:
        '''
        The URL of the master M3U file.
        
        Args:
            quality (Quality): The video quality.
        
        Returns:
            str: The M3U url.
        '''
        
        from ..locals import Quality
        
        # Get qualities
        qualities = {int(v): q['videoUrl']
                     for q in self.fetch('page@mediaDefinitions')
                     if str(v := q['quality']).isdigit()}
        
        logger.info('Extracted %s qualities from %s', len(qualities), self)
        
        return Quality(quality).select(qualities)

    def get_segments(self, quality: Quality) -> Iterator[str]:
        '''
        Get the video segment URLs.
        
        Args:
            quality (Quality): The video quality.
        
        Returns:
            Iterator: A segment URL iterator.
        '''
        
        # Fetch the master file
        master_url = self.get_M3U_URL(quality)
        master_src = self.client.call(master_url).text
        
        urls = [l for l in master_src.split('\n')
                if l and not l.startswith('#')]
        
        if len(urls) != 1:
            raise errors.ParsingError('Multiple index files found.')
        
        # Get DNS address
        dns = master_url.split('master.m3u8')[0]
        
        # Fetch the index file
        url = urls[0]
        raw = self.client.call(dns + url).text
        
        # Parse files
        for line in raw.split('\n'):
            if line.strip() and not line.startswith('#'):
                yield dns + line
    
    def download(self,
                 path: os.PathLike,
                 quality: Quality | str = 'best',
                 *,
                 downloader: Callable[[Video,
                                       Quality,
                                       Callable[[int, int], None],
                                       str], None] = download.default,
                 display: Callable[[int, int], None] = display.default()) -> str:
        '''
        Download the video to a file.
        
        Args:
            path (str): The download path.
            quality (Quality | str | int): The video quality.
            downloader (Callable): The download backend.
            display (Callable): The progress display.
        
        Returns:
            str: The downloader video path.
        '''
        
        # Add a name if the path is a directory
        if os.path.isdir(path):
            path = utils.concat(path, self.key + '.mp4')

        logger.info('Starting download for %s at %s', self, path)

        # Call the backend
        downloader(
            video = self,
            quality = quality,
            callback = display,
            path = path
        )
        
        return path
    
    # === Interaction methods === #
    
    def _assert_internal_success(self, res: dict) -> None:
        '''
        Assert an internal response has succeeded.
        '''
        
        if res['success'] and not res['success'] in ('true', True, 1):
            raise Exception(f'Failed to call : `{res.get("message")}`')
    
    @cached_property
    def _as_query(self) -> dict[str, str]:
        '''
        Simulate a query to gain access to more data.
        
        Warning - This will make a lot of requests and can false
                   some properties (like watched).
        '''
        
        # 1. Create playlist
        name = f'temp-{random.randint(0, 100)}'
        logger.info('Creating temporary playlist %s', name)
        res = self.client.call('playlist/create', 'POST', dict(
            title = name,
            tags = '["porn"]',
            description = '',
            status = 'private',
            token = self._token
        )).json()
        
        self._assert_internal_success(res)
        playlist_id = res.get('id')
        
        # 2. Add to playlist
        res = self.client.call('playlist/video_add', 'POST', dict(
            pid = playlist_id,
            vid = self.id,
            token = self._token
        ))
        
        self._assert_internal_success(res.json())
        
        # 3. Start query
        from .query import queries
        query = queries.VideoQuery(self.client, f'playlist/{playlist_id}')
        raw = query._get_page(0)[0]
        
        keys = ('id', 'key', 'title', 'image', 'preview', 'markers')
        data = {k: v for k, v in zip(keys, consts.re.eval_video(raw))} | {'raw': raw}
        
        # 4. Delete playlist
        logger.info('Deleting playlist %s', name)
        res = self.client.call('playlist/delete', 'POST', dict(
            pid = playlist_id,
            token = self._token,
            action = 'delete'
        ))
        
        return data
    
    def like(self, toggle: bool = True) -> None:
        '''
        Set the video like value.
        Args:
            toggle (bool): The toggle value.
        '''
        
        self.client.call('video/rate', 'POST', dict(
            id = self.id,
            current = self.likes.up,
            value = int(toggle),
            token = self._token
        ))
    
    def favorite(self, toggle: bool = True) -> None:
        '''
        Set video as favorite or not.
        Args:
            toggle (bool): The toggle value.
        '''
        
        res = self.client.call('video/favourite', 'POST', dict(
            toggle = int(toggle),
            id = self.id,
            token = self._token
        ))
        
        self._assert_internal_success(res.json())

    def watch_later(self, toggle: bool = True) -> None:
        '''
        Add or remove the video to the watch later playlist.
        Args:
            toggle (bool): The toggle value.
        '''
        
        mod = 'add' if toggle else 'remove'
        
        res = self.client.call(f'playlist/video_{mod}_watchlater', 'POST',
                               dict(vid = self.id, token = self._token))
        
        self._assert_internal_success(res.json())
    
    # === Data properties === #

    @cached_property
    def _token(self) -> str:
        '''
        The page client token.
        '''
        
        assert self.client.logged, 'Account is not logged in'
        
        # Force fetch page
        self.fetch('page@title')
        
        return consts.re.get_token(self.page)

    @cached_property
    def id(self) -> str:
        '''
        The internal video id.
        '''

        if id_ := self.data.get('page@id'):
            return id_
        
        # Use thumbnail URL 
        return consts.re.get_thumb_id(self.image.url)

    @cached_property
    def title(self) -> str:
        '''
        The video title.
        '''
        
        return (self.data.get('page@title')  # Use page title if cached
                or self.fetch('data@title')) # Use HubTraffic by default

    @cached_property
    def image(self) -> Image:
        '''
        The video thumbnail.
        '''
        
        return Image(client = self.client,
                     url = self.fetch('data@thumb'),
                     servers = self.fetch('data@thumbs'),
                     name = f'thumb-{self.key}')
    
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
        
        params = ('seconds', 'minutes', 'hours', 'days')
        
        # Parse date
        raw = self.fetch('data@duration')
        digits = list(map(int, raw.split(':')))[::-1]
        delta = {k: v for k, v in zip(params, digits)}
        
        return timedelta(**delta)
    
    @cached_property
    def tags(self) -> list[Tag]:
        '''
        The video tags.
        '''
        
        return [Tag(tag['tag_name'])
                for tag in self.fetch('data@tags')]
    
    @cached_property
    def likes(self) -> Like:
        '''
        Positive and negative reviews of the video.
        '''
        
        rating = self.fetch('data@rating') / 100
        counter = self.fetch('data@ratings')
        
        return Like(up = round(rating * counter),
                    down = round((1 - rating) * counter),
                    ratings = rating)
    
    @cached_property
    def views(self) -> int:
        '''
        How many people watched the video.
        '''
        
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
        
        return [User.get(self.client, ps['pornstar_name'])
                for ps in self.fetch('data@pornstars')]
    
    @cached_property
    def categories(self) -> Iterator[Category]:
        '''
        The categories of the video.
        '''
        
        from ..locals import Category
        
        raw = self.fetch('data@categories')
        
        for item in raw:
            
            constant = utils.make_constant(name := item['category'])
            cat = getattr(Category, constant, None)
            
            if cat is None:
                logger.warning('Category not found: %s. You should update PHUB locals (python -m phub update_locals)', constant)
                
                # Create temporary category
                cat = Param('*', name)
            
            yield cat

    @cached_property
    def orientation(self) -> LiteralString:
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
    def liked(self) -> NotImplemented:
        '''
        Whether the video was liked by the account.
        '''
        
        return NotImplemented
    
    @cached_property
    def watched(self) -> bool:
        '''
        Whether the video was viewed previously by the account.
        '''
        
        if not self.client.logged:
            raise Exception('Client must be logged in to use this property.') # temp class
        
        # If we fetched the video page while logged in, PH consider we have watched it
        if self.page:
            return True
        
        if 'watchedVideo' in self._as_query['markers']:
            return True
        
        # For some reason the watched text is different in playlists
        if 'class="watchedVideoText' in self._as_query['raw']:
            return True
    
    @cached_property
    def is_free_premium(self) -> bool | NotImplemented:
        '''
        Whether the video is part of free premium.
        '''
        
        return 'phpFreeBlock' in self._as_query['markers']

    @cached_property
    def preview(self) -> Image | NotImplemented:
        '''
        The preview 'mediabook' of the video.
        This is the lazy video displayed when hovering the video.
        '''
        
        return Image(client = self.client,
                     url = self._as_query['preview'],
                     name = f'preview-{self.key}')
        
    @property
    def is_favorite(self) -> bool:
        '''
        Whether the video has been set as favorite by the client.
        '''
        
        # Make sure page is loaded
        self._token
        
        return bool(consts.re.is_favorite(self.page, False))
# EOF