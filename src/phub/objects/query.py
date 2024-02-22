from __future__ import annotations

import json
import logging
from functools import cache, cached_property
from typing import TYPE_CHECKING, Iterator, Any, Self, Callable

from phub.objects import NO_PARAM, Param

from . import Video, User, FeedItem, Param, NO_PARAM

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client

logger = logging.getLogger(__name__)

QueryItem = Video | FeedItem | User


class Query:
    '''
    A Base query.
    '''
    
    BASE: str = None
    
    def __init__(self,
                 client: Client,
                 func: str,
                 args: dict[str] = {},
                 container_hint: consts.WrappedRegex | Callable = None,
                 query_repr: str = None) -> None:
        '''
        Initialise a new query.
        
        Args:
            client           (Client): The parent client.
            func                (str): The URL function.
            args               (dict): Arguments.
            container_hint (Callable): An hint function to help determine where should the target container be.
            query_repr          (str): Indication for the query representation.
        '''

        self.client = client
        self.hint = container_hint
        self._query_repr = query_repr
        
        # Build URL
        args |= {'page': '{page}'}
        self.url = utils.concat(self.BASE, func, utils.urlify(args))
        
        self.suppress_spicevids = True
        
        logger.debug('Initialised new query %s', self)
    
    def __repr__(self) -> str:
        
        s = f'"{self._query_repr}"' if self._query_repr else f'url="{self.url}"'
        return f'phub.Query({s})'
    
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
                i += 1
                
                yield self._iter_page(page)
                
            except errors.NoResult:
                return
    
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
               watched: bool | None = None,
               free_premium: bool | None = None) -> Iterator[QueryItem]:
        '''
        Get a sample of the query.
        
        Args:
            max           (int): Maximum amount of items to fetch.
            filter   (Callable): A filter function that decides whether to keep each QueryItems.
            watched      (bool): Whether videos should have been watched by the account or not.
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
        
        req = self.client.call(self.url.format(page = index + 1),
                               throw = False)
        
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
                logger.error('Invalid API response from `%s`', self.url)
                raise errors.ParsingError('Invalid API response')

            return videos
        
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
        
        def _eval_video(self, raw: str) -> dict:
            # Evaluate video data.
            # Can be used externally from this query
            
            keys = ('id', 'key', 'title', 'image', 'preview', 'markers')
            data = {k: v for k, v in zip(keys, consts.re.eval_video(raw))} | {'raw': raw}
            
            return data
        
        def _parse_item(self, raw: str) -> Video:
            
            # Parse data
            data = self._eval_video(raw)
            
            url = f'{consts.HOST}view_video.php?viewkey={data["key"]}'
            obj = Video(self.client, url)
            
            # Override the _as_query property since we already have a query 
            obj._as_query = data
            
            # Parse markers
            # markers = ' '.join(consts.re.get_markers(data['markers'])).split()
            
            obj.data = {
                # Property overrides
                'page@title': data["title"],
                'data@thumb': data["image"],
                'page@id': id,
                
                # Custom query properties
                'query@parent': self
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
                if not(self.suppress_spicevids
                    and 'premiumIcon' in wrapped._as_query['markers']):
                    yield wrapped
                
                else:
                    logger.info('Bypassed spicevid video: %s', wrapped)

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