'''
### Objects for the PHUB package. ###
'''

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self, Callable, Generator, Any
if TYPE_CHECKING: from phub.core import Client

import os
import json
from functools import cached_property
from datetime import datetime, timedelta

Soup = None
try:
    from bs4 import BeautifulSoup as Soup

except ModuleNotFoundError:
    print('Warning: BS4 not installed. Feed features will not be available.')

from phub import utils
from phub import consts
from phub import parser
from phub.utils import (log,
                        register_properties,
                        download_presets as dlp)


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
        
        Args:
            video (Video): Video the user has been grabbed from.
        
        Returns:
            User: The video author.
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
        Fetch a user knowing its channel name.
        
        Args:
            client (Client): Client that handles requests.
            url (str): The URL of the user's channel.
            name (str): The name of the user (experimental).
        
        Returns:
            User: The fetched user.
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
            raise consts.UserNotFoundError(f'User `{name}` not found.')
    
    @cached_property
    def videos(self) -> Query:
        '''
        Get the list of videos published by this user.
        Returns:
            Query: The received query.
        '''
        
        url = consts.regexes.sub_root('', self.path)
        if '/model' in self.path: url += '/videos'
        
        return Query(
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

@register_properties
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
        
        Args:
            client (Client): The session client.
            url (str): The video URL.
            preload (bool): Wether to load the video page.
        '''
        
        # assert consts.regexes.is_valid_video_url(url), 'Invalid URL' # TODO - DOES NOT WORK FOR CERTAIN VIDS
        
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
        Load of refresh video page and data.
        '''
        
        # Clear the cache
        log('Video', 'Clearing cache of', self, level = 4)
        for name in self.__properties__:
            if name in self.__dict__:
                delattr(self, name)
        
        # Refresh data
        log('video', 'Refreshing video', self, level = 4)
        response = self.client._call('GET', self.url)
        
        self.page = response.text
        self.data = parser.resolve(self)
    
    def _lazy(self) -> dict:
        '''
        Refresh the video data or get it from the cache.
        
        Returns:
            dict: Parsed video data, fresh from Pornhub.
        '''
        
        print('lazying')
        if not self.data: self.refresh()
        return self.data
    
    # ========= Download ========= #
    
    def get_M3U(self,
                quality: utils.Quality | str | int,
                process: bool = True) -> str | list[str]:
        '''
        Get the M3U file for a certain quality.
        
        Args:
            quality (utils.Quality): Desired video quality.
            process (bool): Wether to parse the file.
        
        Returns:
            str: The raw M3U file if process was False.
            list[str]: The list of video URLs.
        '''
        
        # Try to create a quality object (if the param is already an object
        # it gets immediatly returned)
        quality = utils.Quality(quality)
        
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
        
        # Fetch the master file
        raw = self.client._call('GET', url_base + url, simple_url = False).text
        
        if not process:
            # Just inject the URLs and return the file
            choice = (url_base, '')
            return '\n'.join(choice[line.startswith('#')] + line
                             for line in raw.split('\n') if line)
        
        # Parse all URLs
        segments = [url_base + segment for segment in utils.extract_urls(raw)]
        log('video', f'Parsed {len(segments)} video segments', level = 3)
        return segments

    def download(self,
                 path: str,
                 quality: utils.Quality | str | int,
                 callback: Callable = dlp.bar(),
                 max_retries: int = 5) -> str:
        '''
        Download the video locally.
        
        Note - If path is a directory, it will create a new
        file in that directory with the video title.
        
        Args:
            path (str): Directory or file to write to.
            quality (utils.Quality): Desired video quality.
            callback (Callable): Function to call for progrss updates.
            max_retries (int): Maximum retries per segment until we skip it.
        
        Returns:
            str: The path of the created file.
        '''
        
        log('video', f'Downloading {self} at', path, level = 5)
        
        # Append name if path is directory
        if os.path.isdir(path):
            path += ('' if path.endswith('/') else '/') + utils.pathify(self.title) + '.mp4'
            log('video', f'Changing path to', path, level = 2)
        
        log('downl', 'Starting video download for', self)
        
        segments = self.get_M3U(quality, process = True)
        
        # Unwrap callback if nescessarry
        if callback.__name__ == '__wrapper__':
            callback = callback()
        
        # Start downloading
        with open(path, 'wb') as output:
            
            for index, url in enumerate(segments):
                log('downl', f'Downloading {index + 1}/{len(segments)}', level = 3, r = 0) # TODO
                callback(index + 1, len(segments))
                
                for i in range(max_retries):
                    res = self.client._call('GET', url, simple_url = False, throw = False)
                    
                    if not res.ok:                        
                        log('downl', f'Segment download failed, retrying ({i}/{max_retries})', level = 1)
                        continue
                    
                    output.write(res.content)
                    break
        
        # Stop
        callback(len(segments), len(segments)) # Make sure full progress is registered
        log('downl', 'Successfully downloaded video at', path)
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

class Query:
    '''
    Represent a generator with list-like properties that
    contains `Video` objects.
    
    Example usage:
    
    .. code-block:: python
    
        query = client.search('hello, world!')
        
        # Get a specific video
        first_result = query[0]
        
        # Get a range of videos
        for video in query[:10]:
            print(video.title)
        
        # List all videos
        for video in query:
            print(video.title)
    '''
    
    def __init__(self, client: Client, url: str, corrector: Callable = None) -> None:
        '''
        Generate a new video iterator object.
        
        Args:
            client (Client): The session client.
            url (str): The query page URL.
            corrector (Callable): Parsing corrector.
        '''
        
        log('query', 'Initialising new Query object', level = 6)
        
        self.client = client
        self.url = (url + '?&'['?' in url] + 'page=').replace(consts.ROOT, '')
        
        self._length: int = None
        self.index = 0
        self.page_index: int = None
        self.videos: list[str] = None
        self.page: str = None
        self.corrector = corrector
    
    def __len__(self) -> int:
        '''
        Get the amount of videos.
        
        Returns:
            int: The amount of videos in the `Query` object.
        '''
        
        if self._length: return self._length
        
        # Load 1st page to get the counter
        if self.page is None:
            self._get_page(0)
        
        # Try to find the counter
        counter = consts.regexes.video_search_counter(self.page)
        log('query', 'Collected counters:', counter, level = 4)
        
        if len(counter) != 1: raise consts.CounterNotFound()
        self._length = int(counter[0]) 
        return self._length
    
    def __getitem__(self, index: int | slice) -> Video | Generator[Video, None, None]:
        '''
        Get a specific video or a slice of them.
        
        Args:
            index (int | slice): The index or slice.
        
        Returns:
            Video: A specific video
            Generator: A generator containing videos.
        '''   

        if isinstance(index, int):
            return self.get(index)
        
        def wrapper(): # We need to wrap this, otherwise the whole __getitem__ will be
                       # Interpreted as a generator.
            
            for i in index.indices(self.length):
                yield self.get(i)
        
        return wrapper()
    
    def get(self, index: int) -> Video:
        '''
        Get a specific video using an index.

        Args:
            index (int): The index of the video.
        
        Returns:
            Video: The specific video.
        '''
        
        log('query', 'Getting video at index', index, level = 5)
        
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
        log('query', 'Generated video object')
        video.data = {'video_title': title} # Inject title
        return video

    def _get_page(self, index: int) -> None:
        '''
        Load a page to the temporary query cache.
        
        Args:
            index: The index of the page.
        '''
        
        # If cached, avoid scrapping again
        if self.page_index == index: return
        
        log('query', 'Fetching page at index', index, level = 4)
        raw = self.client._call('GET', self.url + str(index + 1)).text
        
        # Parse videos
        self.page = raw
        self.page_index = index
        self.videos = consts.regexes.extract_videos(raw)
        
        # Correct videos
        if self.corrector is not None:
            log('query', 'Correcting video regex parsing', level = 6)
            self.videos = self.corrector(self.videos)
            
        log('query', f'Collected {len(self.videos)} videos', level = 6)

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
            log('query', 'Reached end of generation')
            raise StopIteration
        
        self.index += 1
        return result

@dataclass
class FeedItem:
    type: consts.FeedType
    content: str = field(repr = False)
    author: str = field(repr = False)
    url: str = field(repr = False)
    date: str = field(repr = False)

class Feed:
    
    def __init__(self, client: Client) -> None:
        '''
        Generate a new feed object.
        
        Args:
            client: The session client.
        '''

        self.client = client
        self.cache: dict[int, list[FeedItem]] = {}
    
    def _get_page(self, page: int) -> list[FeedItem]:
        '''
        Fetch a specific feed page.
        
        Args:
            page: The page index.
        
        Returns:
            list: A list of exactly 14 Feed items.
        '''
        
        # Fetch and parse page
        url = 'feeds'
        if page > 0: url += f'_ajax?ajax=1&page={page + 1}'
        raw = self.client._call('GET', url).text
        
        soup = Soup(raw, 'html.parser')
        sections: list[Soup] = soup.find_all('section', {'class': 'feedItemSection'})
        
        items = []
        for section in sections:
            
            badge = section.find('span', {'class': 'usernameBadgesWrapper'})
            stream = section.find('a', {'class': 'stream_link'})
            
            author = None
            if badge:
                author = User.get(client = self.client,
                                  url = badge.find('a').get('href'))
            
            url = date = None
            if stream:
                url = stream.get('href')
                date = stream.text
            
            content = section.find('div', {'class': 'feedInfo'}).text
            if date: content = content.replace(date, '')
            
            items += [FeedItem(
                type = section.get('data-table'),
                content = utils.hard_strip(content),
                author = author,
                url = url,
                date = utils.hard_strip(date)
            )]
        
        # Save to cache
        self.cache[page] = items
        return items

    def get(self, index: int) -> FeedItem:
        '''
        Get a specific feed item.
        
        Args:
            index: The feed element index.
        
        Returns:
            FeedItem: The feed item object.
        '''
        
        page_index = index // 14
        
        page = self.cache.get(page_index)
        if page is None:
            page = self._get_page(page_index)
        
        return page[ index % 14 ]

# EOF