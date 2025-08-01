from __future__ import annotations

import json
import logging
from base_api.base import setup_logger
from functools import cache, cached_property
from typing import TYPE_CHECKING, Iterator, Any, Callable, Union

from . import Video, User, FeedItem

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client


QueryItem = Union[Video, FeedItem, User]

class Pages:
    '''
    An iterator for query pages.
    '''

    def __init__(self, query: Query) -> None:
        '''
        Initialise a new Pages object.
        '''
        
        self.query = query
    
    def __repr__(self) -> str:
        
        return f'phub.Pages(query={self.query})'
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Iterator[QueryItem], Iterator[Iterator[QueryItem]]]:
        '''
        Get a single, or slice of pages.
        '''
        
        if isinstance(index, int):
            items = self.query._get_page(index)
            return self.query._iter_page(items)
        
        def wrap():
            try:
                # Implementation of a slice range
                i = index.start or 0
                while not index.stop or i < index.stop:
                    yield self[i]
                    i += index.step or 1
            
            except errors.NoResult:
                return
        
        return wrap()
    
    def __iter__(self) -> Iterator[Iterator[QueryItem]]:
        '''
        Iterate each page.
        '''
                
        return self[:]

class Query:
    '''
    A Base query.
    '''
    
    BASE: str = None
    
    def __init__(self,
                 client: Client,
                 func: str,
                 args: dict[str] = {},
                 container_hint: Union[consts.WrappedRegex, Callable] = None,
                 query_repr: str = None) -> None:
        '''
        Initialise a new query.
        
        Args:
            client (Client): The parent client.
            func (str): The URL function.
            args (dict): Arguments.
            container_hint (Callable): An hint function to help determine where should the target container be.
            query_repr (str): Indication for the query representation.
        '''

        self.logger = setup_logger(name="PHUB API - [Query]", log_file=None, level=logging.ERROR)
        self.client = client
        self.hint = container_hint
        self._query_repr = query_repr
        
        # Build URL
        args |= {'page': '{page}'}
        self.url = utils.concat(self.BASE, func, utils.urlify(args))
        
        self.suppress_spicevids = True
        
        self.logger.debug('Initialised new query %s', self)
    
    def __repr__(self) -> str:
        
        s = f'"{self._query_repr}"' if self._query_repr else f'url="{self.url}"'
        return f'phub.Query({s})'

    def enable_logging(self, log_file: str = None, level=None, log_ip=None, log_port=None):
        self.logger = setup_logger(name="PHUB API - [Query]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

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
    def pages(self) -> Pages:
        '''
        Iterate through the query pages.
        '''
        
        return Pages(self)
    
    def __iter__(self) -> Iterator[QueryItem]:
        '''
        Iterate through the query items.
        '''
        
        for page in self.pages:
            for item in page:
                yield item
    
    def sample(self,
               max: int = 0,
               filter: Callable[[QueryItem], bool] = None,
               watched: Union[bool, None] = None,
               free_premium: Union[bool, None] = None) -> Iterator[QueryItem]:
        '''
        Get a sample of the query.
        
        Args:
            max (int): Maximum amount of items to fetch.
            filter (Callable): A filter function that decides whether to keep each QueryItems.
            watched (bool): Whether videos should have been watched by the account or not.
            free_premium (bool): Whether videos should be free premium or not.
        
        Returns:
            Iterator: Response iterator containing QueryItems.
        '''
        
        i = 0
        for item in self:
            # Maximum sample size
            if max and i >= max: return
            
            # Custom filters
            if ((watched is not None and watched != item.watched)
                or (free_premium is not None and free_premium != item.is_free_premium)
                or (filter and not filter(item))): continue
            
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
        url = self.url.format(page = index + 1)
        req = self.client.call(url, get_response=True, throw=False)
        
        if req.status_code == 404:
            raise errors.NoResult()
        
        return req.text
    
    @cache
    def _get_page(self, index: int) -> list:
        '''
        Get split unparsed page items.
        
        Args:
            index (int): The page index:
        
        Returns:
            list: a semi-parsed representation of the page.
        '''
        
        raw = self._get_raw_page(index)
        els = self._parse_page(raw)
        
        if not len(els):
            raise errors.NoResult()
        
        return els

    def _iter_page(self, page: list[str]) -> Iterator[QueryItem]:
        '''
        Wraps and iterate a page items.
        '''
        
        for item in page:
            yield self._parse_item(item)

    #@override
    def _parse_item(self, raw: Any) -> QueryItem:
        '''
        Get a single query item.
        
        Args:
            raw (Any): The unparsed item.
        
        Returns:
            QueryItem: The item object representation.
        '''
        
        return NotImplemented
    
    #@override
    def _parse_page(self, raw: str) -> list[Any]:
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
            video.data = {f'data@{k}': v for k, v in data.items()} | {'query@parent': self}
            
            return video
        
        def _parse_page(self, raw: str) -> list[dict]:
            
            data = json.loads(raw)
            videos = data.get('videos')
            if data.get('code') == '2001':
                raise errors.NoResult()

            elif videos is None:
                print(raw)
                raise errors.ParsingError('Invalid API response')

            return videos
        
        def sample(self, max: int = 0, filter: Callable[[QueryItem], bool] = None) -> Iterator[QueryItem]:
            return super().sample(max, filter)

    class VideoQuery(Query):
        '''
        Represents a Query able to parse HTML data.
        '''
        
        BASE = consts.HOST
        
        def _eval_video(self, raw: str) -> dict:
            # Evaluate video data.
            # Can be used externally from this query
            
            html_entries = consts.re.eval_video(raw)
            html_public_entries = consts.re.eval_public_video(raw, False) or ()
            
            data =        {k: v for v, k in zip(html_entries, ('id', 'key', 'title', 'image'))}
            public_data = {k: v for v, k in zip(html_public_entries, ('preview', 'markers'))}
            
            return {'mediabook': None, 'markers': ''} | data | public_data | {'raw': raw}
        
        def _parse_item(self, raw: str) -> Video:
            
            # Parse data
            data = self._eval_video(raw)
            
            url = f'{consts.HOST}view_video.php?viewkey={data["key"]}'
            obj = Video(self.client, url)
            
            # Override the _as_query property since we already have a query 
            obj._as_query = data
            
            obj.data = {
                # Property overrides
                'page@video_title': data["title"],
                'data@thumb': data["image"],
                'page@id': id,
                
                # Custom query properties
                'query@parent': self,
                'query@watched': 'videos/recent' in self.url
            }
            
            return obj
        
        def _parse_page(self, raw: str) -> list:
            container = (self.hint or consts.re.container)(raw)
            return consts.re.get_videos(container)
    
        def _iter_page(self, page: list[str]) -> Iterator[QueryItem]:
            
            for item in page:
                wrapped: QueryItem = self._parse_item(item)

                # Yield each object of the page, but only if it does not have the spicevids
                # markers and we explicitely suppress spicevids videos.
                if not(self.suppress_spicevids and 'premiumIcon' in wrapped._as_query['markers']):
                    yield wrapped
                
                else:
                    pass # Don't ask.

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
            container = (self.hint or consts.re.container)(raw)
            return consts.re.get_users(container)
        
        def _iter_page(self, page: list[str]) -> Iterator[QueryItem]:
        
            for item in page:
                yield self._parse_item(item)

    class FeedQuery(Query):
        '''
        Represents a query able to parse user feeds.
        '''
        
        BASE = consts.HOST
        
        def _parse_item(self, raw: tuple) -> FeedItem:
            return FeedItem(self.client, raw)
        
        def _parse_page(self, raw: str) -> list[tuple]:
            return consts.re.feed_items(raw)

    class EmptyQuery(Query):
        '''
        Represents an empty query.
        '''
        
        def __init__(self, *args, **kwargs) -> None:
            pass
        
        def __len__(self) -> int:
            return 0
        
        @cached_property
        def pages(self):
            return []

# EOF