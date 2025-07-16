from __future__ import annotations

import logging
from functools import cached_property
from base_api.base import setup_logger
from typing import TYPE_CHECKING, Callable, Iterator, Union

from .. import literals
from . import User, FeedItem

if TYPE_CHECKING:
    from . import queries
    from ..core import Client


class Feed:
    '''
    Represents the account feed.
    '''
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise a new feed object.
        
        Args:
            client (Client): Client parent.
        '''
        
        self.client = client
        self.logger = setup_logger(name="PHUB API - [Feed]", log_file=None, level=logging.ERROR)
        self.logger.debug('Initialised account feed: %s', self)

    def enable_logging(self, log_file: str = None, level=None, log_ip=None, log_port=None):
        self.logger = setup_logger(name="PHUB API - [Feed]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    def __repr__(self) -> str:
        
        return f'phub.FeedCreator(for={self.client.account.name})'
    
    def filter(self,
               section: literals.section = None,
               user: Union[User, str] = None) -> queries.FeedQuery:
        '''
        Creates a Feed Query with specific filters.
        
        Args:
            section (str): Filter parameters.
            user (User | str): User to filter feed with.
        '''
        
        from . import queries
        
        # Generate args
        username = user.name if isinstance(user, User) else user
        
        self.logger.info('Generating new filter feed using args', )
        
        return queries.FeedQuery(
            client = self.client,
            func = 'feeds',
            args = {
                'username': username,
                'section': section
            }
        )
    
    @cached_property
    def feed(self) -> queries.FeedQuery:
        '''
        A feed query with no filters.
        '''

        return self.filter()
    
    # Mimic feed.feed to avoid repetition
    def __iter__(self) -> queries.FeedQuery:
        
        return iter(self.feed)
    
    def sample(self, max: int = 0, filter: Callable[[FeedItem], bool] = None) -> Iterator[FeedItem]:
        '''
        Wraps sampling the global feed.
        
        Args:
            max (int): Maximum amount of items to fetch.
            filter (Callable): A filter function that decides whether to keep each FeedItems.
        
        Returns:
            Iterator: Response iterator containing FeedItems.
        '''
        
        return self.feed.sample(max, filter)

# EOF