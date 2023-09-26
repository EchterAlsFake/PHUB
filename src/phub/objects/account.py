from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Self, Union

from .. import consts
from . import User, Image

if TYPE_CHECKING:
    from ..core import Client
    from . import Feed, HQuery

logger = logging.getLogger(__name__)


class Account:
    '''
    Represents a connected Ponhub account,
    capable of accessing account-only features.
    If the login fails, will be None.
    '''
    
    def __new__(cls, client: Client) -> Union[Self, None]:
        '''
        Check if the object creation is needed.
        '''
        
        if all(client.credentials.values()):
            logger.info('Creating new account object')
            return object.__new__(cls)
        
        logger.info('Bypassing account creation, no credentials')
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise a new account object.
        '''
        
        self.client = client
        
        self.name: str = None
        self.avatar: Image = None
        self.is_premium: bool = None
        self.user: User = None
        
        # Save data keys so far so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        
        logger.info('Account object %s created', self)
        
    def __repr__(self) -> str:
        
        status = 'logged-out' if self.name is None else f'name={self.name}' 
        return f'phub.Account({status})'

    def connect(self, data: dict) -> None:
        '''
        Update account data once login was successful.
        '''
        
        self.name = data.get('username')
        self.avatar = Image(self.client, data.get('avatar'), 'avatar')
        self.is_premium = data.get('premium_redirect_cookie') != '0'
        
        url = consts.HOST + f'/users/{self.name}'
        self.user = User(client = self.client, name = self.name, url = url)
        
        # We assert that the account is from a normal user (not model, etc.)
        if not 'users/' in self.user.url:
            logger.error('Invalid user type: %s', url)
            raise NotImplementedError('Non-user account are not supported.')
    
    def refresh(self, refresh_login: bool = False) -> None:
        '''
        Delete the object's cache to allow items refreshing.
        '''
        
        logger.info('Refreshing account %s', self)
        
        if refresh_login:
            logger.info('Forcing login refresh')
            self.client.login(force = True)
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                
                logger.debug('Deleting key %s', key)
                delattr(self, key)
    
    @cached_property
    def recommended(self) -> HQuery:
        '''
        Videos recommended to the account.
        '''
        
        from . import HQuery
        
        return HQuery(self.client, 'recommended')
    
    @cached_property
    def watched(self) -> HQuery:
        '''
        Account video history.
        '''
        
        from . import HQuery
        
        return HQuery(self.client, f'users/{self.name}/videos/recent')
    
    @cached_property
    def liked(self) -> HQuery:
        '''
        Videos liked by the account.
        '''
        
        from . import HQuery
        
        return HQuery(self.client, f'users/{self.name}/videos/favorites')
    
    @cached_property
    def feed(self) -> Feed:
        '''
        The account feed.
        '''
        
        from . import Feed

        return Feed(self.client)
    
    # TODO - Recommended users /user/discover/popular_verified_members

# EOF