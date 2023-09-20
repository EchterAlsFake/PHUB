from __future__ import annotations

from typing import TYPE_CHECKING
from functools import cached_property

if TYPE_CHECKING:
    from ..core import Client
    from ..locals import Section

from . import FQuery, User, Param, NO_PARAM


class Feed:
    '''
    Represents the account feed.
    '''
    
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
        
        raw_args = args.gen()
        
        if raw_args.startswith('&'):
            raw_args = raw_args.replace('&', '?', 1)
        
        return FQuery(self.client, self.url + raw_args)
    
    @cached_property
    def feed(self) -> FQuery:
        '''
        A feed query with no filters.
        '''

        return self.filter()

# EOF