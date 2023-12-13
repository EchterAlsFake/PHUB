from __future__ import annotations

import json
import logging
from functools import cache, cached_property
from typing import TYPE_CHECKING, Iterator, Any, Self, Callable

from . import Video, User, FeedItem, Param, NO_PARAM, Pornstar

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client

logger = logging.getLogger(__name__)

QueryItem = Video | FeedItem | User | Pornstar


class Query:
    '''
    A Base query.
    '''
    
    BASE: str = None
    
    def __init__(self, client: Client, func: str, param: Param = NO_PARAM) -> None:
        '''
        Initialise a new query.
        
        Args:
            client (Client): The parent client.
            func      (str): The URL function.
            param   (Param): Filter parameter.
        '''

        self.client = client
        
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
    
    def __len__(self) -> int:
        '''
        Attempts to fetch the query length.
        '''
        
        raw = self._get_raw_page(0)
        counter = consts.re.query_counter(raw, throw = False)
                
        if counter is None:
            raise IndexError('This Query does not support len()')

        return int(counter)

    @cached_property
    def pages(self) -> Iterator[Iterator[QueryItem]]:
        '''
        Iterate through the query pages.
        '''
        
        i = 0
        while 1:
            
            try:
                page = self._get_page(i)
            
            except errors.NoResult:
                return
            
            i += 1
            yield (self._parse_item(item) for item in page)
    
    def __iter__(self) -> Self:
        '''
        Iterate through the query items.
        '''
        
        for page in self.pages:
            for item in page:
                yield item
    
    def sample(self, max: int = 0, filter: Callable[[QueryItem], bool] = None) -> Iterator[QueryItem]:
        '''
        Get a sample of items.
        '''
        
        i = 0
        for item in self:
            
            if max and i >= max:
                return
            
            if filter and not filter(item):
                continue
            
            i += 1
            yield item
    
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
            raw (str): The raw page container.
        
        Returns:
            list: A semi-parsed list representation.
        '''
        
        return NotImplemented

class queries:
    '''
    A collection of all PHUB queries.
    '''
    
    class JSONQuery(Query):
        '''
        Represents a query able to parse JSON data from the HubTraffic API.
        '''
        
        BASE = consts.API_ROOT
        
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
        
        def sample(self, max: int = 0, filter: Callable[[QueryItem], bool] = None) -> Iterator[QueryItem]:
            return super().sample(max, filter)

    class VideoQuery(Query):
        '''
        Represents a Query able to parse HTML data.
        '''
        
        BASE = consts.HOST
        
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
        
        def _parse_page(self, raw: str) -> list:
            container = consts.re.container(raw)
            return consts.re.get_videos(container)

    class UserQuery(VideoQuery):
        '''
        Represents an advanced member search query.
        '''
        
        def _parse_item(self, raw: tuple) -> User:
            
            url, image_url = raw
            
            obj = User.get(self.client, utils.concat(consts.HOST, url))
            obj._cached_avatar_url = image_url # Inject image url
            return obj

        def _parse_page(self, raw: str) -> list[tuple]:
            container = consts.re.container(raw)
            return consts.re.get_users(container)

    class FeedQuery(Query):
        '''
        Represents a query able to parse user feeds.
        '''
        
        BASE = consts.HOST
        
        def _parse_item(self, raw: tuple) -> FeedItem:
            return FeedItem(self.client, raw)
        
        def _parse_page(self, raw: str) -> list[tuple]:
            return consts.re.feed_items(raw)

'''
TODO:
    - User/Model/Pornstar videos enum
    - Pornstars personnal videos
    - Account recommendations
    - Feed
'''

# EOF