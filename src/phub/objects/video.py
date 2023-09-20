from __future__ import annotations

import os
import shutil
from datetime import datetime, timedelta

from typing import TYPE_CHECKING, Generator, LiteralString, Callable
from functools import cached_property

if TYPE_CHECKING:
    from ..core import Client
    from ..locals import Quality

from . import Tag, Like, User, Image
from .. import utils
from .. import errors
from .. import consts
from ..modules import download, parser, display


class Video:
    '''
    Represents a Pornhub video.
    '''
    
    # === Base methods === #
    
    def __init__(self, client: Client, url: str) -> None:
        '''
        Initialise a new video object.
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
    
    def __repr__(self) -> str:
        
        return f'phub.Video(key={self.key})'
        
    def refresh(self, page: bool = True, data: bool = True) -> None:
        '''
        Refresh video data.
        '''
        
        # Clear saved video page and data 
        if page: self.page = None
        if data: self.data.clear()
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                delattr(self, key)
     
    def fetch(self, key: str) -> None:
        '''
        Lazily fetch some data.
        
        data@key => Use webmasters
        page@key => Use web scraper
        '''
        
        if key in self.data:
            return self.data.get(key)
        
        # Fetch only webmasters data
        if key.startswith('data@'):
            
            url = utils.concat(consts.API_ROOT, 'video_by_id?id=' + self.key)
            data = self.client.call(url).json()
            self.data |= {f'data@{k}': v for k, v in data['video'].items()}
        
        # Fetch raw page
        elif key.startswith('page@'):
            
            self.page = self.client.call(self.url).text
            data = parser.resolve(self)
            self.data |= {f'page@{k}': v for k, v in data.items()}
        
        return self.data.get(key)

    # === Download methods === #
    
    def get_M3U_URL(self, quality: Quality) -> str:
        '''
        The URL of the master M3U file.
        '''
        
        from ..locals import Quality
        
        # Get the quality master file
        qualities = {
            int(el['quality']): el['videoUrl']
            for el in self.fetch('page@mediaDefinitions')
            if el['quality'] in ['1080', '720', '480', '240']
        }
        
        return Quality(quality).select(qualities)

    def get_segments(self, quality: Quality) -> Generator[str, None, None]:
        '''
        Get the video segment URLs.
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
                 path: str,
                 quality: Quality | str = 'best',
                 *,
                 downloader: Callable = download.default,
                 display: Callable = display.default(),
                 **kwargs) -> str:
        '''
        Download the video to a file.
        '''
        
        if os.path.isdir(path):
            path = utils.concat(path, self.key + '.mp4')

        # Call the backend
        video = downloader(client = self.client,
                           video = self,
                           quality = quality,
                           callback = display,
                           **kwargs)
        
        if isinstance(video, str):
            # Move to file
            shutil.move(video, path)
        
        else:
            # Write to file
            with open(path, 'wb') as output:
                output.write(video)
        
        return path
    
    # === Data properties === #

    @cached_property
    def title(self) -> str:
        '''
        The video title.
        '''
        
        if title := self.data.get('data@title'):
            return title
        
        if title := self.data.get('page@title'):
            return title
        
        return self.fetch('data@title')

    @cached_property
    def image(self) -> Image:
        '''
        The video thumbnail.
        '''
        
        return Image(client = self.client,
                     url = self.fetch('data@thumb'),
                     sizes = self.fetch('data@thumbs'),
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
    def like(self) -> Like:
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
    def hotspots(self) -> Generator[int, None, None]:
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
        return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S') # TODO check if %d-%m or %m-%d
        
    @cached_property
    def pornstars(self) -> list[User]:
        '''
        The pornstars present in the video.
        '''
        
        return [User(ps['pornstar_name'])
                for ps in self.fetch('data@pornstars')]
    
    @cached_property
    def categories(self) -> list[NotImplemented]:
        '''
        The categories of the video.
        '''
        
        raw = self.fetch('data@categories')
        
        return raw # TODO

    @cached_property
    def segment(self) -> LiteralString:
        '''
        Video segment (e.g. straight).
        '''
        
        return self.fetch('data@segment')
    
    @cached_property
    def author(self) -> User:
        '''
        The video's author.
        '''
        
        return User.from_video(self)

# EOF