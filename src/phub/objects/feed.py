from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from functools import cached_property

from . import User, Param, NO_PARAM

from .. import utils

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
        '''
        
        self.client = client
        
        logger.debug('Initialised account feed: %s', self)
    
    def filter(self,
               section: Section | Param | str = NO_PARAM,
               user: User | str = None) -> FQuery: # TODO - Unify multiple types for all constants
        '''
        Creates a Feed Query with specific filters.
        '''
        
        from . import FQuery
        
        # Generate args
        args = section.gen() | {'username': user.name if isinstance(user, User) else user}
        
        raw = utils.urlify(args)
        
        logger.info('Generating new filter feed using args `%s`', raw)
        return FQuery(self.client, 'feeds' + raw)
    
    @cached_property
    def feed(self) -> FQuery:
        '''
        A feed query with no filters.
        '''

        return self.filter()

# EOF