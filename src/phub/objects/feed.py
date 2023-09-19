from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Client
    from ..locals import Section

from . import FQuery, User, Param, NO_PARAM


class Feed:
    '''
    Represents the account feed.
    '''
    
    PAGE_LENGTH = 0
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise a new feed object.
        '''
        
        self.client = client
        self.url = 'feeds'
        
    def filter(self,
               section: Section | Param | str = None,
               user: User | str = None) -> FQuery: # TODO - Unify multiple types for all constants
        '''
        Creates a Feed Query with specific filters.
        '''
        
        # Generate args
        args = NO_PARAM
        if section: args += section
        if user: args += Param('username', user.name if isinstance(user, User) else user)
        
        return FQuery(self.client, self.url + args.gen().replace('&', '?', 1))

# EOF