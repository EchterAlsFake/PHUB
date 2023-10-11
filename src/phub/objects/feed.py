from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union
from functools import cached_property

from . import User, Param, NO_PARAM

if TYPE_CHECKING:
    from ..core import Client
    from ..locals import Section
    from . import FQuery

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
    
    def filter(self,
               section: Union[Section, Param, str] = NO_PARAM,
               user: Union[User, str] = None) -> FQuery:
        '''
        Creates a Feed Query with specific filters.
        
        Args:
            section (Section | Param | str): Filter parameters.
            user (User | str): User to filter feed with.
        '''
        
        from . import FQuery
        
        # Generate args
        username = user.name if isinstance(user, User) else user
        
        logger.info('Generating new filter feed using args', )
        return FQuery(self.client, 'feeds', Param('username', username) | section)
    
    @cached_property
    def feed(self) -> FQuery:
        '''
        A feed query with no filters.
        '''

        return self.filter()

# EOF