from __future__ import annotations

import json
import logging
from functools import cache
from typing import TYPE_CHECKING, Generator, Any

from . import (Video, User, FeedItem,
               Param, NO_PARAM)

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client

logger = logging.getLogger(__name__)

QueryItem = Video | FeedItem | User


class Query:
    '''
    A Base query for type hints that handles
    getting items. 
    '''
    
    BASE: str = None
    PAGE_LENGTH: int = None
    
    def __init__(self, client: Client, func: str, param: Param = NO_PARAM) -> None:
        '''
        Initialise a new query.
        
        Args:
            client (Client): The parent client.
            func      (str): The URL function.
            param   (Param): Filter parameter.
        '''

        self.client = client
        self.iter_index = -1

        # Parse param
        param |= Param('page', '{page}')
        self.url = utils.concat(self.BASE, func)
        
        add_qm = True
        for key, set_ in param.value.items():
            self.url += '&?'[add_qm]
            nk, ns = self._parse_param_set(key, set_)
            self.url += f'{nk}={ns}'
            add_qm = False
        
        logger.debug('Initialised new query %s', self)
    
    def __repr__(self) -> str:
        
        return f'phub.Query(url={self.url})'
    
    def __getitem__(self, index: int | slice) -> QueryItem | Generator[QueryItem, None, None]:
        '''
        Get one or multiple items from the query.
        '''
        
        assert isinstance(index, (int, slice))
        
        if isinstance(index, int):
            return self.get(index)

        def wrap() -> Generator[Video, None, None]:
            # Support slices
            
            for i in range(index.start or 0,
                           index.stop  or 0,
                           index.step  or 1):
                
                yield self.get(i)
        
        return wrap()

    def __len__(self) -> int:
        '''
        Attempts to fetch the query length.
        '''
        
        raw = self._get_raw_page(0)
        counter = consts.re.query_counter(raw, throw = False)
                
        if counter is None:
            raise IndexError('This Query does not support len()')

        return int(counter)

    def __iter__(self):
        
        self.iter_index = -1
        return self
    
    def __next__(self):
        
        try:
            self.iter_index += 1
            return self.get(self.iter_index)
        
        except errors.NoResult:
            raise StopIteration

    @cache
    def get(self, index: int) -> QueryItem:
        '''
        Get a single item.
        
        Args:
            index (int): The item index.
        
        Returns:
            QueryItem: The item as an object representation.
        '''
        
        assert isinstance(index, int)
        
        # Support negative values
        if index < 0:
            index = len(self) - index

        page = self._get_page(index // self.PAGE_LENGTH)
        
        if len(page) > (ii := index % self.PAGE_LENGTH):
            return self._parse_item(page[ii])
        
        raise errors.NoResult('Item does not exist')
    
    @cache
    def _get_raw_page(self, index: int) -> str:
        '''
        Get the raw page.
        
        Args:
            index (int): The page index.
        
        Returns:
            str: The raw page content.
        '''
        
        assert isinstance(index, int)
        
        req = self.client.call(self.url.format(page = index + 1),
                               throw = False)
        
        if req.status_code == 404:
            raise errors.NoResult()

        return req.text
    
    @cache
    def _get_page(self, index: int) -> list:
        '''
        Get splited unparsed page items.
        
        Args:
            index (int): The page index:
        
        Returns:
            list: a semi-parsed representation of the page.
        '''
        
        raw = self._get_raw_page(index)
        return self._parse_page(raw)
    
    # Methods defined by subclasses
    def _parse_param_set(self, key: str, set_: set) -> tuple[str, str]:
        '''
        Parse param set.
        
        Args:
            key  (str): The parameter key.
            set_ (set): The parameter value.
        
        Returns:
            tuple: The final key and raw value.
        '''
        
        set_ = [v.split('@')[1] if '@' in v else v for v in set_]
        
        raw = '|'.join(set_)
        return key, raw

    def _parse_item(self, raw: Any) -> QueryItem:
        '''
        Get a single query item.
        
        Args:
            raw (Any): The unparsed item.
        
        Returns:
            QueryItem: The item object representation.
        '''
        
        return NotImplemented
    
    def _parse_page(self, raw: str) -> list:
        '''
        Get a query page.
        
        Args:
            raw (str): The unparsed page.
        
        Returns:
            list: A semi-parsed list representation.
        '''
        
        return NotImplemented


class JQuery(Query):
    '''
    Represents a query able to parse JSON data.
    '''
    
    BASE = consts.API_ROOT
    PAGE_LENGTH = 30
    
    def _parse_item(self, data: dict) -> Video:
        
        # Create the object and inject data
        video = Video(self.client, url = data['url'])
        video.data = {f'data@{k}': v for k, v in data.items()}
        
        return video
    
    def _parse_page(self, raw: str) -> list[dict]:
        
        data = json.loads(raw).get('videos')

        if data is None:
            logger.error('Invalif API response from `%s`', self.url)
            raise errors.ParsingError('Invalid API response')

        return data

class HQuery(Query):
    '''
    Represents a Query able to parse HTML data.
    '''
    
    BASE = consts.HOST
    PAGE_LENGTH = 32
    
    def _parse_param_set(self, key: str, set_: set) -> tuple[str, str]:
        
        if key == 'category':
            key = 'filter-category'
        
        set_ = [v.split('@')[0] if '@' in v else v for v in set_]
        
        raw = '|'.join(set_)
        return key, raw
    
    def _parse_item(self, raw: tuple) -> Video:
                
        url = f'{consts.HOST}view_video.php?viewkey={raw[0]}'
        
        obj = Video(self.client, url)
        obj.data = {f'page@title': raw[2]}
        
        return obj
    
    def _parse_page(self, raw: str) -> list[tuple]:
                
        container = raw.split('class="container')[1]
        return consts.re.get_videos(container)

class UQuery(HQuery):
    '''
    Represents a Query able to parse User video data.
    '''
    
    PAGE_LENGTH = 40
    
    def _parse_page(self, raw: str) -> list[tuple]:
        
        container = raw.split('class="videoSection')[1]
        return consts.re.get_videos(container)

class FQuery(Query):
    '''
    Represents a query able to parse user feeds.
    '''
    
    BASE = consts.HOST
    PAGE_LENGTH = 13 # Unsure
    
    def _parse_item(self, raw: tuple) -> FeedItem:
        
        return FeedItem(self.client, raw)
    
    def _parse_page(self, raw: str) -> list[tuple]:
        return consts.re.feed_items(raw)

class MQuery(HQuery):
    '''
    Represents an advanced member search query.
    '''
    
    PAGE_LENGTH = 42
    
    def _parse_item(self, raw: tuple) -> User:
        
        url, image_url = raw
        
        obj = User.get(self.client, utils.concat(consts.HOST, url))
        obj._cached_avatar_url = image_url # Inject image url
        return obj

    def _parse_page(self, raw: str) -> list[tuple]:
        
        container = raw.split('id="advanceSearchResultsWrapper')[1]
        return consts.re.get_users(container)

class PQuery(MQuery):
    '''
    Represents a pornstar search query.
    '''
    
    PAGE_LENGTH = 16
    
    def _parse_item(self, raw: tuple) -> User:
        
        avatar, url, name, videos = raw
        
        # Create new user
        obj = User(self.client,
                   name = name,
                   type = 'pornstar',
                   url = url)
        
        obj._cached_avatar_url = avatar # Inject avatar
        
        return obj
    
    def _parse_page(self, raw: str) -> list[tuple]:
        
        container = raw.split('id="pornstarsSearchResult')[1].split('</ul')[0]
        return consts.re.get_ps(container)

class SQuery(Query):
    
    PAGE_LENGTH = 37
    
    def _parse_item(self, raw: Any) -> User:
        
        return NotImplemented
    
    def _parse_page(self, raw: str) -> list:
        
        container = raw.split('<div id="profileContent">')[1]
        return NotImplemented
        
    

# EOF