'''
Core module of the PHUB package.
'''

from __future__ import annotations
from io import TextIOWrapper
from typing import Self

import json
import requests
from functools import cached_property

from phub import utils
from phub import consts
from phub import classes
from phub.utils import log


class Account:
    '''
    Represent a Client's account.
    '''
    
    def __new__(cls, client: Client) -> Self:
        '''
        Verify that user has entered credentials.
        Returns None if no account used.
        '''
        
        if client._intents_to_login:
            return object.__new__(cls)
        
        log('accnt', 'Passing account creation')
    
    def __init__(self, client: Client) -> None:
        '''
        Generate a new Account object.
        '''
        
        self.client = client
        self.name = self.client.creds['username']
        
        log('accnt', 'Initialised new account', repr(self))
    
    def __repr__(self) -> str:
        return f'<phub.core.Account name={self.name}>'
    
    @cached_property
    def recommended(self) -> classes.VideoIterator:
        '''
        Get the recommended videos.
        '''
        
        return classes.VideoIterator(self.client, consts.ROOT + 'recommended')
        
    @cached_property
    def watched(self) -> classes.VideoIterator:
        '''
        get the account watched videos.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/recent'
        return classes.VideoIterator(self.client, url, corrector = utils.remove_video_ads)

    @cached_property
    def liked(self) -> classes.VideoIterator:
        '''
        get the account favorite videos.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/favorites'
        return classes.VideoIterator(self.client, url, corrector = utils.remove_video_ads)

class Client:
    '''
    Represents a Client capable of interacting with PornHub.
    '''
    
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 session: requests.Session = None,
                 autologin: bool = False) -> None:
        '''
        Initialise a new client.
        '''
        
        # Initialise session
        self.session = session or requests.Session()
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        
        self.creds = {'username': username, 'password': password}
        self._intents_to_login = bool(username)
        
        # Connect Account object
        self.account: Account | None = Account(self)
        
        # Autologin
        self.logged = False
        if autologin: self.login()
        
        log('client', 'Initialised new client', repr(self))

    def __repr__(self) -> str:
        status = 'anonymous', 'connect (' + ('not ', '')[self.logged] + 'logged)'
        return f'<phub.Client {status[self._intents_to_login]}>'
    
    @classmethod
    def from_file(cls, data: str | dict | TextIOWrapper) -> Self:
        '''
        Generate a new client from credentials.
        '''
        
        if isinstance(data, TextIOWrapper):
            data = data.read()
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            
            except json.JSONDecodeError or AssertionError:
                raise ValueError('Invalid json file.')
        
        if isinstance(data, dict):
            if data.get('username') and data.get('password'):
                
                log('Initialising client from', type(data), level = 7)
                return cls(**data)
            
            raise KeyError('Data must have username and password keys.')
        
        raise TypeError('Invalid type for data:', type(data))
    
    def _call(self,
              method: str,
              func: str,
              headers = {},
              data = None,
              simple_url: bool = True,
              throw: bool = True) -> requests.Response:
        '''
        Make a custom request to PornHub servers.
        '''
        
        url = consts.ROOT + utils.slash(func, '**') \
              if simple_url else func
        
        log('client', f'Sending request at {utils.shortify(url, 25)}', level = 6)
        
        response = self.session.request(
            method = method,
            url = url,
            headers = consts.HEADERS | headers,
            data = data
        )
        
        log('client', 'Request passed with status', response.status_code, level = 6)
        
        if throw and not response.ok:
            raise ConnectionError(f'Request `{func}` failed:',
                                  utils.shortify(response.text))
        
        return response
    
    def login(self, throw: bool = False) -> bool:
        '''
        Attempt to login to PornHub.
        Returns whether the operation was successful.
        
        Arguments
            throw: Raises an error if the connection fails.
        '''
        
        log('client', 'Attempting loggin...', level = 6)
        
        # Extract token
        home = self._call('GET', '/').text
        token = consts.regexes.extract_token(home)
        log('client', 'Extracted token', token, level = 5)
        
        # Send credentials
        log('client', 'Sending payload', level = 5)
        payload = consts.LOGIN_PAYLOAD | self.creds | {'token': token}
        
        response = self._call('POST', 'front/authenticate', data = payload)
        success = int(response.json()['success'])
        
        if success:
            log('client', 'Login successful!', level = 6)
        
        else:
            log('client', 'Login failed', level = 2)
            
            # Throw error
            if throw:
                raise ConnectionRefusedError('Connection failed. Check credentials.')
        
        self.logged = success
        return success

    def get(self, url: str = None, key: str = None, preload: bool = True) -> classes.Video:
        '''
        Get a specific video using an URL or a viewkey.
        '''
        
        assert bool(url) ^ bool(key)
        
        if key is not None:
            url = consts.ROOT + f'view_video.php?viewkey={key}'
        
        return classes.Video(client = self, url = url, preload = preload)
    
    def get_user(self, name: str) -> classes.User:
        '''
        Attempt to fetch a user knowing its name (raw channel name).
        '''
        
        log('client', 'Fetching user', name, level = 6)
        return classes.User.get(self, name)
    
    def search(self, query: str) -> classes.VideoIterator:
        '''
        Make a research for videos on PornHub servers.
        '''
        
        log('client', 'Opening new search query:', query, level = 6)
        url = consts.ROOT + 'video/search?search=' + query
        return classes.VideoIterator(self.client, url)

# EOF