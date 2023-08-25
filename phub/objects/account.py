
from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import core

from . import User, Image

class Account:
    
    def __new__(cls, client: core.Client) -> Self | None:
        '''
        Check if it is nessescary to create an account object.
        '''
        
        if all(client.credentials.values()):
            return object.__new__(cls)        
    
    def __init__(self, client: core.Client) -> None:
        '''
        Initalise the account.
        '''
        
        self.client = client
        
        self.name: str
        self.avatar: Image
        self.is_premium: bool
        
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
        self.user = User(name = self.name)
    
    def refresh(self) -> None:
        '''
        Delete the object's cache to allow items refreshing.
        '''
        
        pass
    
    def recommended(self):
        pass
    
    def watched(self):
        pass
    
    def liked(self):
        pass
    
    def feed(self):
        pass
        