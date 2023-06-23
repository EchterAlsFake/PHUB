'''
### Objects for the PHUB package. ###
'''

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self, Callable
if TYPE_CHECKING: from phub.core import Client

import os
import json
from functools import cached_property
from datetime import datetime, timedelta

from phub import utils
from phub import consts
from phub import parser
from phub.utils import log, download_presets as dlp

# Errors
class UserNotFoundError(Exception): pass


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
        #### Generate a User object from a Video object. ####
        -----------------------------------------------------
        
        Arguments:
        - `video` -- Video the user has been grabbed from.
        
        -----------------------------------------------------
        Returns a `User` object.
        '''
        
        log('users', 'Searching author of', video, level = 6)
        video._lazy()
        
        # Guess the user is a model/pornstar or channel
        guess = consts.regexes.video_model(video.page) or \
                consts.regexes.video_channel(video.page)
        
        # Invalid user protection
        if not guess:
            raise NotImplementedError(f'User type in {video} invalid or not implemented.')
        
        rel, name = guess[0]
        
        return cls(name = name, path = rel, client = video.client)
    
    @classmethod
    def get(cls,
            client: Client,
            url: str = None,
            name: str = None) -> Self:
        '''
        #### Fetch a user knowing its channel name. ####
        ------------------------------------------------
        
        Arguments:
        - `client`         -- Client that handles requests.
        - `url`  (=`None`) -- URL of the user info.
        - `name` (=`None`) -- Name of the user (Will guess user type) (experimental).
        
        ------------------------------------------------
        Returns a `User` object.
        '''
        
        log('users', 'Initialising new user:', name or url, level = 6)
        
        assert bool(url) ^ bool(name), 'Must specify exactly one of url and name'
        
        # URL case
        if url: return cls(name = url.split('/')[-1],
                           path = url.replace(consts.ROOT, ''),
                           client = client)
        
        for type_ in ('model', 'pornstar', 'channels'):
            
            log('users', 'Guessing user is of type', type_, level = 5)
            
            url = f'{type_}/{name.replace(" ", "-")}'
            response = client._call('GET', url, throw = False)
            
            if response.ok and url.lower() in response.url:
                return cls(name = name, path = url, client = client)
        
        else:
            raise UserNotFoundError(f'User `{name}` not found.')
    
    @property
    def videos(self) -> VideoIterator:
        '''
        #### Get the list of videos published by this user. ####
        --------------------------------------------------------
        Returns a `VideoIterator` object.
        '''
        
        url = consts.regexes.sub_root('', self.path)
        if '/model' in self.path: url += '/videos'
        
        print(url)
        
        return VideoIterator(
            client = self.client,
            url = url,
            corrector = utils.remove_video_ads
        )

@dataclass
class Like:
    '''
    Dataclass representing 'up' and 'down' thumbs for a video.
    '''
    
    up: int
    down: int

@dataclass
class Tag:
    '''
    Dataclass equivalent to one video tag,
    with its 'name' and 'count' (apparitions on PH).
    '''
    
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
        #### Generate a new Video object. ####
        --------------------------------------
        
        Arguments:
        - `client`             -- Client to inherit from.
        - `url`                -- The video URL.
        - `preload` (=`False`) -- Whether to send the video page request.
        '''
        
        assert consts.regexes.is_valid_video_url(url), 'Invalid URL'
        
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
        #### Load of refresh video page and data. ####
        '''
        
        log('video', 'Refreshing video', self, level = 4)
        response = self.client._call('GET', self.url)
        
        self.page = response.text
        self.data = parser.resolve(self.page)
    
    def _lazy(self) -> dict:
        '''
        #### Refresh the video data or get it from the cache. ####
        ----------------------------------------------------------
        Returns a `dict` object containing the parsed video data.
        '''
        
        if not self.data: self.refresh()
        return self.data
    
    # ========= Download ========= #

    def get_M3U(self,
                quality: utils.Quality,
                process: bool = True) -> str | list[str]:
        '''
        #### Get the raw M3U url for a certain quality. ####
        ----------------------------------------------------
        
        Arguments:
        - `quality`           -- The desired quality as an object.
        - `process` (=`True`) -- Whether to parse the file.
        
        ----------------------------------------------------
        Returns a list of segment URLs if `process` is `True`,
        else the URL of the M3U file.
        '''
        
        assert isinstance(quality, utils.Quality), 'Quality must be Quality object'
        
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
                 quality: utils.Quality,
                 callback: Callable = dlp.bar(),
                 max_retries: int = 5) -> str:
        '''
        #### Download the video locally. ####
        -------------------------------------
        
        Arguments:
        - `path`               -- Directory or file to write to.
        - `quality`            -- Desired video quality.
        - `callback` (=`None`) -- Function to call to update download progress.
        - `max_retries` (=`5`) -- Maximum retries per segment request.
        
        NOTE 1 - If `path` is a directory, will create a new file in that directory
                 with the name of the video.
        NOTE 2 - Slow download. To use threaded downloads, call `get_M3U` instead.
        NOTE 3 - Glitchy logs.
        -------------------------------------
        Returns the path of the file.
        '''
        
        log('video', f'Downloading {self} at', path, level = 5)
        
        # Append name if path is directory
        if os.path.isdir(path):
            path += ('' if path.endswith('/') else '/') + utils.pathify(self.title) + '.mp4'
            log('video', f'Changing path to', path, level = 2)
        
        log(' D L ', 'Starting video download for', self)
        
        segments = self.get_M3U(quality, process = True)
        
        # Start downloading
        with open(path, 'wb') as output:
            
            for index, url in enumerate(segments):
                log(' D L ', f'Downloading {index + 1}/{len(segments)}', level = 3, r = 0) # TODO
                if callback: callback(index + 1, len(segments))
                
                for i in range(max_retries):
                    res = self.client._call('GET', url, simple_url = False, throw = False)
                    
                    if not res.ok:                        
                        log(' D L ', f'Segment download failed, retrying ({i}/{max_retries})', level = 1)
                        continue
                    
                    output.write(res.content)
                    break
        
        # Stop
        log(' D L ', 'Successfully downloaded video at', path)
        return path
    
    # ======== Properties ======== #
    
    @cached_property
    def title(self) -> str:
        '''
        The title of the video.
        '''
        
        return self._lazy().get('video_title')
    
    @cached_property
    def image_url(self) -> str:
        '''
        Thumbnail URL of the video. Use client.session.get to download.
        '''
        
        return self._lazy().get('image_url')
    
    @cached_property
    def is_vertical(self) -> bool:
        '''
        Whether the video is in vertial mode.
        '''
        
        return bool(self.lazy().get('isVertical'))
    
    @cached_property
    def duration(self) -> timedelta:
        '''
        Video duration as a timedelta object.
        '''
        
        secs = self._lazy().get('video_duration')
        return timedelta(seconds = secs)
    
    @cached_property
    def tags(self) -> list[Tag]:
        '''
        Tags of the video.
        '''
        
        return [Tag(*tag.split(':')) for tag in
                self._lazy().get('actionTags').split(',') if tag]

    @cached_property
    def like(self) -> Like:
        '''
        Positive and negative likes of the video.
        '''
        
        self._lazy()
        
        votes = {t.lower(): v for t, v in consts.regexes.video_likes(self.page)}
        return Like(votes['up'], votes['down'])

    @cached_property
    def views(self) -> int:
        '''
        How many times the video has been watched.
        '''

        self._lazy()

        raw = consts.regexes.video_interactions(self.page)[0]
        return int(json.loads(f'[{raw}]')[0]['userInteractionCount'].replace(' ', '').replace(',', ''))
    
    @cached_property
    def hotspots(self) -> list[int]:
        '''
        List of hotspots (in seconds) of the video.
        '''
        
        return list(map(int, self._lazy().get('hotspots')))

    @cached_property
    def date(self) -> datetime:
        '''
        The publish date of the video as a datetime object.
        '''
        
        self._lazy()
        raw: str = consts.regexes.extract_video_date(self.page)[0]
        return datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S%z')

    @cached_property
    def author(self) -> User:
        '''
        Get the author of the video.
        '''
        
        return User.from_video(self)

class VideoIterator:
    '''
    Represent a generator with list-like properties that
    contains `Video` objects.
    
    Example usage:
    ```python
    record = VideoIterator(...)
    
    first = record[0] # list-like index searching
    count = len(record) # Get length of the record
    
    # Using generation
    for video in record:
        print(video.title)
        
    # Get all videos
    everything = list(record)
    ```
    '''
    
    def __init__(self, client: Client, url: str, corrector: Callable = None) -> None:
        '''
        #### Generate a new video iterator object. ####
        -----------------------------------------------
        
        Arguments:
        - `client`              -- The client to base from.
        - `url`                 -- The URL of the page that contains the playlist.
        - `corrector` (=`None`) -- Function to call to correct parsing in edge cases.
        '''
        
        log('viter', 'Initialising new Video Iterator', level = 6)
        
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
        #### Get the amount of distributed videos. ####
        Can also be called using the `len()` built-in.
        
        NOTE - Implemented only for `client.search()`.
        
        -----------------------------------------------
        Returns an `ìnt` containing the amount of videos
        in the `VideoIterator` object.
        '''
        
        # Load a page to get the counter
        if self._length is None: self._get_page(0)
        return self._length
    
    def get(self, index: int) -> Video:
        '''
        #### Get a specific video using an index. ####
        Can also be addressed with __getitem__.
        
        ----------------------------------------------
        Arguments:
        - `index` -- The index of the video.
        
        ----------------------------------------------
        Returns a `Video` object.
        '''
        
        log('viter', 'Getting video at index', index, level = 5)
        
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
        log('viter', 'Generated video object')
        video.data = {'video_title': title} # Inject title
        return video

    def _get_page(self, index: int) -> None:
        '''
        #### Get a specific page by index. ####
        ---------------------------------------
        
        Arguments:
        - `index` -- The index of the page.
        '''
        
        # If cached, avoid scrapping again
        if self.page_index == index: return
        
        log('viter', 'Fetching page at index', index, level = 4)
        raw = self.client._call('GET', self.url + str(index + 1)).text
        
        # Define counter
        if self._length is None:
            counter = consts.regexes.video_search_counter(raw)
            
            if not counter:
                log('viter', 'Counter collection failed', level = 2)
                self._length = 0 # did not found counter TODO
            
            else:
                self._length = int(counter[0])
                log('viter', 'Collected counter:', self._length, level = 4)
        
        # Parse videos
        self.page = raw
        self.page_index = index
        self.videos = consts.regexes.extract_videos(raw)
        
        # Correct videos
        if self.corrector is not None:
            log('viter', 'Correcting video regex parsing', level = 6)
            self.videos = self.corrector(self.videos)
            
        log('viter', f'Collected {len(self.videos)} videos', level = 6)

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
            log('viter', 'Reached end of generation')
            raise StopIteration
        
        self.index += 1
        return result
        
# EOF
