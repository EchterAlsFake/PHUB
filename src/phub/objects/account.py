from __future__ import annotations

import logging
from functools import cached_property
from base_api.base import setup_logger
from typing import TYPE_CHECKING, Literal, Iterator, Union

from .. import utils
from .. import consts
from . import User, Image

if TYPE_CHECKING:
    from ..core import Client
    from . import Feed, queries, User


class Account:
    '''
    Represents a connected Ponhub account,
    capable of accessing account-only features.
    If the login fails, there will be None.
    '''
    
    def __new__(cls, client: Client) -> Union[object, None]:
        '''
        Check if the object creation is needed.
        
        Args:
            client (Client): The client that initialized this.
        
        Returns:
            Self: The Account object or None, if login is not triggered.
        '''
        
        if all(client.credentials.values()):
            return object.__new__(cls)
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise a new account object.
        
        Args:
            client (Client): The client parent.
        '''
        
        self.client = client
        self.logger = setup_logger(name="PHUB API - [Account]", log_file=None, level=logging.ERROR)
        
        self.name: str = None
        self.avatar: Image = None
        self.is_premium: bool = None
        self.user: User = None
        
        # Save data keys so far, so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']

    def enable_logging(self, log_file: str = None, level=None, log_ip=None, log_port=None):
        self.logger = setup_logger(name="PHUB API - [Account]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    def __repr__(self) -> str:
        status = 'logged-out' if self.name is None else f'name={self.name}' 
        return f'phub.Account({status})'

    def connect(self, data: dict) -> None:
        '''
        Update account data once login was successful.
        
        Args:
            data (dict): Data fetched from the login request.
        '''
        
        self.name = data.get('username')
        self.avatar = Image(self.client, data.get('avatar'), name = 'avatar')
        self.is_premium = data.get('premium_redirect_cookie') != '0'
        
        url = consts.HOST + f'/users/{self.name}'
        self.user = User(client = self.client, name = self.name, url = url)
        
        # We assert that the account is from a normal user (not model, etc.)
        if not 'users/' in self.user.url:
            self.logger.error('Invalid user type: %s', url)
            raise NotImplementedError('Non-user account are not supported.')
    
    def refresh(self, refresh_login: bool = False) -> None:
        '''
        Delete the object's cache to allow items refreshing.
        
        Args:
            refresh_login (bool): Whether to also attempt to re-log in.
        '''
        
        self.logger.info('Refreshing account %s', self)
        
        if refresh_login:
            self.logger.info('Forcing login refresh')
            self.client.login(force = True)
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                
                self.logger.debug('Deleting key %s', key)
                delattr(self, key)
    
    def fix_recommendations(self) -> None:
        '''
        Allow recommendations cookies.
        '''
        
        self.logger.info('Fixing account recommendations')
        
        payload = utils.urlify({
            'token': self.client._granted_token,
            'cookie_selection': 3,
            'site_id': 1
        })
        
        res = self.client.call('user/log_user_cookie_consent' + payload, silent = True)
        
        assert res.json().get('success')
    
    @cached_property
    def recommended(self) -> queries.VideoQuery:
        '''
        Videos recommended to the account.
        '''
        
        from . import queries
        
        # Called each account refresh
        self.fix_recommendations()
        
        return queries.VideoQuery(self.client, 'recommended')
    
    @cached_property
    def watched(self) -> queries.VideoQuery:
        '''
        Account video history.
        '''
        
        from . import queries
        
        return queries.VideoQuery(self.client, f'users/{self.name}/videos/recent')
    
    @cached_property
    def liked(self) -> queries.VideoQuery:
        '''
        Videos liked by the account.
        '''
        
        from . import queries
        
        return queries.VideoQuery(self.client, f'users/{self.name}/videos/favorites')
    
    @cached_property
    def subscriptions(self) -> Iterator[User]:
        '''
        Get the account subscriptions.
        '''
        
        page = self.client.call(f'users/{self.name}/subscriptions')
        
        for url, avatar in consts.re.get_users(page.text):
            
            obj = User.get(self.client, utils.concat(consts.HOST, url))
            obj._cached_avatar_url = avatar # Inject image url
            
            yield obj
    
    @cached_property
    def feed(self) -> Feed:
        '''
        The account feed.
        '''
        
        from . import Feed

        return Feed(self.client)
    
    def dictify(self,
                keys: Union[Literal['all'], list[str]] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.
        
        Returns:
            dict: Dict version of the object.
        '''
        
        return utils.dictify(self, keys, ['name', 'avatar',
                                          'is_premium', 'user'], recursive)

# EOF