'''
Object representation for the PHUB package.
'''

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self, Callable
if TYPE_CHECKING: from phub.core import Client

import os
import json
from datetime import datetime
from functools import cached_property

from phub import utils
from phub import consts
from phub import parser
from phub.utils import log

@dataclass
class User:
    '''
    Represents a PornHub account.
    '''
    
    name: str
    path: str = field(repr = False)
    client: Client = field(repr = False)
    
    @classmethod
    def from_video(cls, video: Video) -> Self:
        '''
        Generate a User object from a Video object.
        '''
        
        log('users', 'Searching author of', video, level = 6)
        video._lazy()
        
        name = consts.regexes.video_author(video.page)
        
        if not name:
            log('users', 'Regex searching failed', level = 1)
            return
        
        return cls(
            name = name,
            path = 'users/' + name,
            client = video.client
        )
    
    @classmethod
    def get(cls, client: Client, name: str) -> Self:
        '''
        Fetch a user knowing its channel name.
        '''
        
        log('users', 'Initialising new user:', name, level = 6)
        
        return cls(
            name = name,
            path = f'users/{name}',
            client = client
        )
    
    @property
    def videos(self) -> VideoIterator:
        '''
        Get the list of videos published by this user.
        '''
        
        raise NotImplemented

@dataclass
class Like:
    up: int
    down: int

@dataclass
class Tag:
    name: str
    count: int = field(repr = False)

class Video:
    '''
    Represent a PornHub video.
    '''
    
    # ======= Base methods ======= #
    
    def __init__(self,
                 client: Client,
                 url: str,
                 preload: bool = False) -> None:
        '''
        Generate a new Video object.
        '''
        
        assert consts.regexes.is_valid_video_url(url)
        
        # Build URL
        self.url = utils.basic(url, False)
        self.key = url.split('=')[-1]
        
        log('video', 'Initialising new video:', self.key, level = 6)
        
        # Video data
        self.client = client
        self.page: str = None
        self.data: dict = None
        
        if preload:
            log('video', 'Preloading video', self, level = 6)
            self.refresh()
    
    def __repr__(self) -> str:
        return f'<phub.Video key={self.key}>'
    
    def refresh(self) -> None:
        '''
        Load of refresh video data.
        '''
        
        log('video', 'Refreshing video', self, level = 4)
        response = self.client._call('GET', self.url)
        
        self.page = response.text
        self.data = parser.resolve(self.page)
        
    def _lazy(self) -> dict:
        '''
        Refresh the page through a cache system.
        '''
        
        if not self.data: self.refresh()
        return self.data
    
    # ========= Download ========= #

    def get_M3U(self,
                quality: consts.Quality,
                process: bool = True) -> str | list[str]:
        '''
        Get the raw M3U url for a certain quality.
        
        process
        True -> list of segmenst
        False -> M3U url
        '''
        
        assert isinstance(quality, consts.Quality)
        
        quals = {int(el['quality']): el['videoUrl']
                 for el in self._lazy()['mediaDefinitions']
                 if el['quality'] in ['1080', '720', '480', '240']}
        
        master = quality.select(quals)
        log('video', 'Selecting quality', utils.shortify(master, 25), level = 4)
        
        # Fetch quality file
        res = self.client._call('GET', master, simple_url = False)
        
        url_base = master.split('master.m3u8')[0]
        url = utils.extract_urls(res.text)[0]
        log('video', 'Extracted', len(url), level = 4)
        
        if not process: return url_base + url
        
        # Fetch and parse master file
        raw = self.client._call('GET', url_base + url, simple_url = False)
        segments = [url_base + segment for segment in utils.extract_urls(raw.text)]
        log('video', f'Parsed {len(segments)} video segments', level = 3)
        return segments

    def download(self,
                 path: str,
                 quality: consts.Quality = None,
                 quiet: bool = False,
                 max_retries: int = 5) -> str:
        '''
        Download the video to a path.
        '''
        
        log('video', f'Downloading {self} at', path, level = 5)
        
        # Append name if path is directory
        if os.path.isdir(path):
            path += ('' if path.endswith('/') else '/') + utils.pathify(self.title) + '.mp4'
            log('video', f'Changing path to', path, level = 2)
        
        
        # Exceptionally allow debugging
        is_logging = utils.DEBUG
        if not quiet: utils.DEBUG = True
        
        log(' D L ', 'Starting video download for', self)
        
        segments = self.get_M3U(quality, process = True)
        
        # Start downloading
        with open(path, 'wb') as output:
            
            for index, url in enumerate(segments):
                log(' D L ', f'Downloading {index + 1}/{len(segments)}', level = 3, r = 1)
                
                for i in range(max_retries):
                    res = self.client._call('GET', url, simple_url = False, throw = False)
                    
                    if not res.ok:                        
                        log(' D L ', f'Segment download failed, retrying ({i}/{max_retries})', level = 1)
                        continue
                    
                    output.write(res.content)
                    break
        
        log(' D L ', 'Successfully downloaded video at', path)
        
        # Reset logging to previous
        utils.DEBUG = is_logging
        return path
    
    # ======== Properties ======== #
    
    @cached_property
    def title(self) -> str: return self._lazy().get('video_title')
    
    @cached_property
    def image_url(self) -> str: return self._lazy().get('image_url')
    
    @cached_property
    def is_vertical(self) -> bool: return bool(self.lazy().get('isVertical'))
    
    @cached_property
    def duration(self) -> int:
        '''Video duration in seconds'''
        
        return self._lazy().get('video_duration')
    
    @cached_property
    def tags(self) -> list[Tag]:
        return [Tag(*tag.split(':')) for tag in
                self._lazy().get('actionTags').split(',') if tag]

    @cached_property
    def like(self) -> Like:
        self._lazy()
        
        votes = {t.lower(): v for t, v in consts.regexes.video_likes(self.page)}
        return Like(votes['up'], votes['down'])
    
    @cached_property
    def views(self) -> int:
        self._lazy()
        
        raw = consts.regexes.video_interactions(self.page)[0]
        return int(json.loads(f'[{raw}]')[0]['userInteractionCount'].replace(' ', ''))
    
    @cached_property
    def hotspots(self) -> list[int]:
        '''
        List of hotspots (in seconds) of the video.
        '''
        
        return list(map(int, self._lazy().get('hotspots')))

    @cached_property
    def date(self) -> datetime:
        '''
        Get the publish date of the video.
        
        raw date format: 2019-07-17T19:28:53+00:00"
        '''
        
        self._lazy()
        raw: str = consts.regexes.extract_video_date(self.page)[0]
        return datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S%z')

    @cached_property
    def author(self) -> User:
        '''
        Get the video's author.
        '''
        
        return User.from_video(self)

class VideoIterator:
    '''
    Represents a playlist of Video objects
    that will be gerenerated on demand.
    '''
    
    def __init__(self, client: Client, url: str, corrector: Callable = None) -> None:
        '''
        Generate a new video iterator object.
        '''
        
        self.client = client
        self.url = (url + '?&'['?' in url] + 'page=').replace(consts.ROOT, '')
        
        self._length: int = None
        self.index = 0
        self.page_index: int = None
        self.videos: list[str] = None
        self.page: str = None
        self.corrector = corrector
    
    def __len__(self) -> int:
        return self.len
        
    def __getitem__(self, index: int) -> Video:
        return self.get(index)    
    
    @property
    def len(self) -> int:
        '''
        Get the amount of distributed videos.
        '''
        
        # Load a page to get the counter
        if self._length is None: self._get_page(0)
        return self._length
    
    def get(self, index: int) -> Video:
        '''
        Get a specific video using an index.
        Can also be addressed with __getitem__.
        '''
        
        # Handle relative indexes
        if index < 0: index += len(self)
        
        page_index = index // 32
        
        # Fetch page if needed
        if self.index != page_index or self.page is None:
            self._get_page(page_index)
        
        # Get the needed video
        key, title = self.videos[ index % 32 ]
        url = consts.ROOT + f'view_video.php?viewkey={key}'
        
        video = Video(client = self.client, url = url, preload = False)
        video.data = {'video_title': title} # Inject title
        return video

    def _get_page(self, index: int) -> None:
        '''
        Get a specific page by index.
        '''
        
        # If cached, avoid scrapping again
        if self.page_index == index: return
        
        raw = self.client._call('GET', self.url + str(index + 1)).text
        
        # Define counter
        if self._length is None:
            counter = consts.regexes.video_search_counter(raw)
            
            if not counter: self._length = 0 # did not found counter TODO
            else: self._length = int(counter[0])
        
        # Parse videos
        self.page = raw
        self.page_index = index
        self.videos = consts.regexes.extract_videos(raw)
        
        # Correct videos
        if self.corrector is not None:
            self.videos = self.corrector(self.videos)

    def __iter__(self) -> Self:
        '''
        Generator initialisation.
        '''
        
        self.index = 0
        return self

    def __next__(self) -> Video:
        '''
        Generator iteration.
        '''
        
        try:
            result = self.get(self.index)
        
        except IndexError:
            raise StopIteration
        
        self.index += 1
        return result
        
# EOF