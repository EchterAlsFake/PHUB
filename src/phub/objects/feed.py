from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Iterator

from . import User, Param, NO_PARAM, FeedItem

if TYPE_CHECKING:
    from . import queries
    from ..core import Client
    from ..locals import Section

logger = logging.getLogger(__name__)


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
        
        logger.debug('Initialised account feed: %s', self)
    
    def __repr__(self) -> str:
        
        return f'phub.FeedCreator(for={self.client.account.name})'
    
    def filter(self,
               section: Section | Param | str = NO_PARAM,
               user: User | str = None) -> queries.FeedQuery:
        '''
        Creates a Feed Query with specific filters.
        
        Args:
            section (Section | Param | str): Filter parameters.
            user (User | str): User to filter feed with.
        '''
        
        from . import queries
        
        # Generate args
        username = user.name if isinstance(user, User) else user
        
        logger.info('Generating new filter feed using args', )
        return queries.FeedQuery(self.client, 'feeds', Param('username', username) | section)
    
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
        return self.feed.sample(max, filter)

# EOF