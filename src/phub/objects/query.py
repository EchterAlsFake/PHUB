from __future__ import annotations

import json
from functools import cache

from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from ..core import Client

from . import Video
from .. import utils
from .. import consts
from .. import errors


class JQuery:
    '''
    Represents a query able to parse JSON data.
    '''
    
    def __init__(self, client: Client, args: str) -> None:
        '''
        Initialise a new query.
        '''

        self.client = client
        self.url = utils.concat(consts.API_ROOT, args) + '&page='
    
    def __getitem__(self, index: int | slice | tuple) -> Video | Generator[Video, None, None] | tuple[Video]:
        '''
        Get one or multiple videos.
        '''
        
        assert isinstance(index, (int, slice, tuple))
        
        if isinstance(index, int):
            return self.get(index)
        
        if isinstance(index, tuple):
            return tuple(self.get(i) for i in index)
        
        def wrap() -> Generator[Video, None, None]:
            # Support slices
            
            for i in range(index.start or 0,
                           index.stop  or 0,
                           index.step  or 1):
                
                yield self.get(i)
        
        return wrap()            
    
    def __repr__(self) -> str:
        
        return f'phub.Query(url={self.url})'
    
    @cache
    def get(self, index: int) -> Video:
        '''
        Get a video at an index.
        '''
        
        assert isinstance(index, int)
        
        data = self._get_page(index // 30)[index % 30]
        
        # Create the object and inject data
        video = Video(self.client, url = data['url'])
        video.data = {f'data@{k}': v for k, v in data.items()} # NOTE - Repetitive w/ Video.fetch
        
        return video
    
    @cache
    def _get_page(self, index: int) -> list[dict]:
        '''
        Fetch a page.
        '''
        
        raw = self.client.call(self.url + str(index + 1)).text
        data = json.loads(raw).get('videos')

        if data is None: raise errors.URLError('Invalid API response')

        return data

class HQuery(JQuery):
    '''
    Represents a Query able to parse HTML data.
    '''
    
    def __init__(self, client: Client, args: str) -> None:
        '''
        Initialise a new query.
        '''
        
        self.client = client
        self.url = utils.concat(consts.HOST, args) + '?&'['?' in args] + 'page='
    
    @cache
    def get(self, index: int) -> Video:
        '''
        Get a single video at an index.
        '''
        
        video = self._get_page(index // 32)[index % 32]
        
        url = f'{consts.HOST}view_video.php?viewkey={video[0]}'
        
        obj = Video(self.client, url)
        obj.data = {f'page@title': video[2]}
        
        return obj
    
    @cache
    def _get_page(self, index: int) -> list[dict]:
        '''
        Fetch a page.
        '''
        
        url = self.url + str(index + 1)
        
        raw = self.client.call(url).text
        
        container = raw.split('class="container')[1]
        
        videos: list = consts.re.get_videos(container)
        
        return videos

# EOF