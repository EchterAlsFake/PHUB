'''
Object representation for the PHUB package.
'''

from __future__ import annotations

from typing import TYPE_CHECKING, Self
from dataclasses import dataclass, field
if TYPE_CHECKING: from phub.core import Client

import os
import json
from datetime import datetime

from phub import utils
from phub import consts
from phub import parser


class User:
    '''
    Represents a PornHub account.
    '''
    
    def __init__(self) -> None:
        '''
        Generate a new User object.
        '''
        pass
    
    @classmethod
    def from_video(cls, video: Video) -> Self:
        '''
        Generate a User object from a Video object.
        '''
        
        pass
    

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
        
        # Video data
        self.client = client
        self.page: str = None
        self.data: dict = None
        self.author = User.from_video(self)
        
        if preload: self.refresh()
    
    def __repr__(self) -> str:
        return f'<phub.Video key={self.key}>'
    
    def refresh(self) -> None:
        '''
        Load of refresh video data.
        '''
        
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
        
        parse
        True -> list of segmenst
        False -> M3U url
        '''
        
        assert isinstance(quality, consts.Quality)
        
        quals = {int(el['quality']): el['videoUrl']
                 for el in self._lazy()['mediaDefinitions']
                 if el['quality'] in ['1080', '720', '480', '240']}
        
        master = quality.select(quals)
        
        # Fetch quality file
        res = self.client._call('GET', master, simple_url = False)
        
        url_base = master.split('master.m3u8')[0]
        url = utils.extract_urls(res.text)[0]
        
        if not process: return url_base + url
        
        # Fetch and parse master file
        raw = self.client._call('GET', url_base + url, simple_url = False)
        return [url_base + segment for segment in utils.extract_urls(raw.text)]

    def download(self,
                 path: str,
                 quality: consts.Quality = None,
                 quiet: bool = False,
                 max_retries: int = 5) -> str:
        '''
        Download the video to a path.
        '''
        
        # Append name if path is directory
        # if not os.path.isfile(path): path += utils.pathify(self.title) # TODO not working
        
        if not quiet: print('[+] Starting donwload for', self)
        
        segments = self.get_M3U(quality, process = True)
        
        # Start downloading
        with open(path, 'wb') as output:
            
            for index, url in enumerate(segments):
                if not quiet: print(f'\r[+] Downloading: {index + 1}/{len(segments)}', end = '')
                
                for i in range(max_retries):
                    res = self.client._call('GET', url, simple_url = False, throw = False)
                    
                    if not res.ok:
                        if not quiet: print(f'\n[-] Failed, retrying ({i})...')
                        continue
                    
                    output.write(res.content)
                    break
        
        if not quiet: print('\n[+] Downloaded video at', path)
        return path
    
    # ======== Properties ======== #
    
    @property
    def title(self) -> str: return self._lazy().get('video_title')
    
    @property
    def image_url(self) -> str: return self._lazy().get('image_url')
    
    @property
    def is_vertical(self) -> bool: return bool(self.lazy().get('isVertical'))
    
    @property
    def duration(self) -> int:
        '''Video duration in seconds'''
        
        return self._lazy().get('video_duration')
    
    @property
    def tags(self) -> list[Tag]:
        return [Tag(*tag.split(':')) for tag in
                self._lazy().get('actionTags').split(',') if tag]

    @property
    def like(self) -> Like:
        self._lazy()
        
        votes = {t.lower(): v for t, v in consts.regexes.video_likes(self.page)}
        return Like(votes['up'], votes['down'])
    
    @property
    def views(self) -> int:
        self._lazy()
        
        raw = consts.regexes.video_interactions(self.page)[0]
        return int(json.loads(f'[{raw}]')[0]['userInteractionCount'].replace(' ', ''))
    
    @property
    def hotspots(self) -> list[int]:
        '''
        List of hotspots (in seconds) of the video.
        '''
        
        return list(map(int, self._lazy().get('hotspots')))


class VideoIterator:
    '''
    Represents a playlist of Video objects
    that will be gerenerated on demand.
    '''
    
    def __init__(self, client: Client, url: str) -> None:
        '''
        Generate a new video iterator object.
        '''
        
        self.client = client
        self.url = (url + '?&'['?' in url] + 'page=').replace(consts.ROOT, '')
        
        self._length: int = None
        
        self.page_index: int = None
        self.videos: list[str] = None
        self.page: str = None
    
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
        if self.index != page_index:
            self._get_page(page_index)
        
        # Get the needed video
        key, title = self.videos[ index % 32 ]
        
        video = Video(key = key, preload = False)
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

# EOF