from __future__ import annotations

import os
import logging
from functools import cached_property
from datetime import datetime, timedelta
from typing import (TYPE_CHECKING, Iterator, Literal,
                    LiteralString, Callable, Any)

from . import (Tag, Like, User,
               Image, Param)
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
            page (bool): Wether to refresh the video page.
            data (bool): Wether to refresh the video data.
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
        Convert the object to a dictionnary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects dictify. 
        
        Returns:
            dict: Dict version of the object.
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
        
    # === Data properties === #

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
        Wether the video is in vertical mode.
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
    
    def _assert_internal_success(self, res: dict) -> None:
        '''
        Assert an internal response has succeeded.
        '''
        
        if not res['success']:
            raise Exception(f'Failed to add to playlist: `{res["message"]}`')
    
    def _set_like(self, value: int) -> None:
        '''
        Set the video like value.
        '''
        
        assert self.client.logged, 'Account is not logged in'
        
        res = self.client.call(f'video/rate?id={self.id}&token={self.client.token}&current={self.likes.up}&value={value}', 'POST')
        
        # self._assert_internal_success(res)
        
        print(res.status_code, res.content)

    def _set_favorite(self, value: int) -> None:
        '''
        Set video as favorite or not.
        '''
        
        # BUG - 400 Invalid for some reason 
        res = self.client.call(func = 'video/favourite',
                               method = 'POST',
                               data = f'toggle={value}&id={self.id}&token={self.client.token}',
                               headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                          'Referer': consts.HOST + '/view_video.php?viewkey=' + self.key})
        
        self._assert_internal_success(res.json())

    def watch_later(self) -> None:
        '''
        Add the video to the watch later playlist.
        '''
        
        res = self.client.call('playlist/video_add_watchlater', 'POST', dict(
            vid = None,
            token = self.client.token
        ))
        
        self._assert_internal_success(res.json())
    
    def like(self) -> NotImplemented:
        '''
        Likes the video.
        '''
        
        self._set_like(1)
    
    def unlike(self) -> NotImplemented:
        '''
        Unlikes the video.
        '''
        
        self._set_like(0)

    @cached_property
    def watched(self) -> bool | NotImplemented:
        '''
        Whether the video was viewed previously by the account.
        
        Warning: In the event you don't get this video from a *page* query,
        calling this could become really unoptimized.
        '''
        
        if not self.client.logged:
            raise Exception('Client must be logged in to use this property.') # temp class
        
        # If we fetched the video page, PH consider we have watched it
        if self.page:
            return True
        
        # If the video was initialised by a query, Pornhub
        # gives us this information so there is no problem
        if markers := self.data.get('query@markers'):
            return 'watchedVideo' in markers
        
        # If the video comes from nowhere, well idk
        # Hack: create a temp PH playlist to simulate a
        # query and get info from there
        return NotImplemented

# EOF