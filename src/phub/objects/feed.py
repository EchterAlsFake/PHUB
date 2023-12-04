from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from functools import cached_property

from . import User, Param, NO_PARAM

if TYPE_CHECKING:
    from . import FeedQuery
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
               user: User | str = None) -> FeedQuery:
        '''
        Creates a Feed Query with specific filters.
        
        Args:
            section (Section | Param | str): Filter parameters.
            user (User | str): User to filter feed with.
        '''
        
        from . import FeedQuery
        
        # Generate args
        username = user.name if isinstance(user, User) else user
        
        logger.info('Generating new filter feed using args', )
        return FeedQuery(self.client, 'feeds', Param('username', username) | section)
    
    @cached_property
    def feed(self) -> FeedQuery:
        '''
        A feed query with no filters.
        '''

        return self.filter()
    
    def __iter__(self) -> FeedQuery:
        
        return iter(self.feed)

# EOF