from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from ..core import Client

from . import User, Image, HQuery
from .. import objects
from .. import consts

class Account:
    
    def __new__(cls, client: Client) -> Self | None:
        '''
        Check if it is necessary to create an account object.
        '''
        
        if all(client.credentials.values()):
            return object.__new__(cls)        
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise the account.
        '''
        
        self.client = client
        
        self.name: str = None
        self.avatar: Image = None
        self.is_premium: bool = None
        self.user: User = None
        
        # Save data keys so far so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        
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
        
        # We assert that the account is from a normal user (not model, etc.)
        
        url = consts.HOST + f'/users/{self.name}'
        self.user = User(client = self.client, name = self.name, url = url)
    
    def refresh(self, refresh_login: bool = False) -> None:
        '''
        Delete the object's cache to allow items refreshing.
        '''
        
        if refresh_login:
            self.client.login(force = True)
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                delattr(self, key)
    
    @cached_property
    def recommended(self) -> HQuery:
        '''
        Videos recommended to the account.
        '''
        
        return HQuery(self.client, 'recommended')
    
    @cached_property
    def watched(self) -> HQuery:
        '''
        Account video history.
        '''
        
        return HQuery(self.client, f'users/{self.name}/videos/recent')
    
    @cached_property
    def liked(self) -> HQuery:
        '''
        Videos liked by the account.
        '''
        
        return HQuery(self.client, f'users/{self.name}/videos/favorites')
    
    @cached_property
    def feed(self) -> NotImplemented:
        '''
        The account feed.
        '''

        return NotImplemented

# EOF