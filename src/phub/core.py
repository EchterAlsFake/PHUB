'''
### Core module of the PHUB package. ###

See https://github.com/Egsagon/PHUB for documentation.
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
        #### Generate a new Account object. ####
        ----------------------------------------
        
        Arguments:
        - `client` -- The client to base the account from.
        '''
        
        self.client = client
        self.name = self.client.creds['username']
        
        log('accnt', 'Initialised new account', repr(self))
    
    def __repr__(self) -> str:
        return f'<phub.core.Account name={self.name}>'
    
    @cached_property
    def recommended(self) -> classes.VideoIterator:
        '''
        #### Get the recommended videos for the user. ####
        --------------------------------------------------
        Returns a `VideoIterator` object.
        '''
        
        return classes.VideoIterator(self.client, consts.ROOT + 'recommended')
        
    @cached_property
    def watched(self) -> classes.VideoIterator:
        '''
        #### Get the history of the user. ####
        --------------------------------------
        Returns a `VideoIterator` object.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/recent'
        return classes.VideoIterator(self.client, url,
                                     corrector = utils.remove_video_ads)

    @cached_property
    def liked(self) -> classes.VideoIterator:
        '''
        #### Get the favorite videos of the account. ####
        -------------------------------------------------
        Returns a `VideoIterator` object.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/favorites'
        return classes.VideoIterator(self.client, url,
                                     corrector = utils.remove_video_ads)

class Client:
    '''
    Represents a Client capable of interacting with PornHub.
    '''
    
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 session: requests.Session = None,
                 language: str = 'en,en-US',
                 autologin: bool = False) -> None:
        '''
        #### Initialise a new client. #####
        -----------------------------------
        
        Arguments
        - `username`     (=`None`) -- Account to connect to username.
        - `password`     (=`None`) -- Account to connect to password.
        - `session`      (=`None`) -- Recovery requests session.
        - `language` (=`en,en-US`) -- Language of the client session.
        - `autologin`   (=`False`) -- Whether to login after initialisation.
        
        -----------------------------------
        Returns a `Client` object.
        '''
        
        # Initialise session
        self.session = session or requests.Session()
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        
        self.creds = {'username': username, 'password': password}
        self._intents_to_login = bool(username)
        self.language = {'Accept-Language': language}
        
        # Connect Account object
        self.account: Account | None = Account(self)
        
        # Autologin
        self.logged = False
        if autologin: self.login()
        
        log('client', 'Initialised new client', repr(self))

    def __repr__(self) -> str:
        '''
        Display Client object representation and informations about
        whether the account is connected.
        '''
        
        status = 'anonymous', 'connect (' + ('not ', '')[self.logged] + 'logged)'
        return f'<phub.Client {status[self._intents_to_login]}>'
    
    def __str__(self) -> str:
        return repr(self)
    
    @classmethod
    def from_file(cls, data: str | dict | TextIOWrapper) -> Self:
        '''
        #### Generate a new client from credentials. ####
        -------------------------------------------------
        
        Arguments:
        - `data` -- Dictionnary, JSON file or JSON string to get
                    username and password from.
        
        -------------------------------------------------
        Returns a `Client` object.
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
        #### Handle sending and receiving custom requests from PornHub servers. ####
        ----------------------------------------------------------------------------
        
        Arguments:
        - `method`               -- Request method (GET, POST, PUT, etc.).
        - `func`                 -- Name and arguments of the PornHub function.
        - `headers`      (=`{}`) -- Optional headers to add.
        - `data`       (=`None`) -- Optional payload to send.
        - `simple_url` (=`True`) -- Whether to consider `func` as a simple Pornhub.
        - `throw`      (=`True`) -- Whether to handle HTTP related errors.
        
        ----------------------------------------------------------------------------
        Returns a `requests.Response` object.
        '''
        
        url = consts.ROOT + utils.slash(func, '**') \
              if simple_url else func
        
        log('client', f'Sending request at {utils.shortify(url, 25)}', level = 6)
        
        response = self.session.request(
            method = method,
            url = url,
            headers = consts.HEADERS | headers | self.language,
            data = data
        )
        
        log('client', 'Request passed with status', response.status_code, level = 6)
        
        if throw and not response.ok:
            raise ConnectionError(f'Request `{func}` failed:' + \
                utils.shortify(response.text))
        
        return response
    
    def login(self, throw: bool = False) -> bool:
        '''
        #### Attempt to login to PornHub. #### 
        ---------------------------------------
        
        Arguments:
        - `throw` (=`False`) -- Raise errors in case of HTTP errors.
        
        ---------------------------------------
        Returns whether the operation was successful.
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
        #### Get a specific video using an URL or a viewkey. ####
        ---------------------------------------------------------
        
        Arguments:
        - `url`      (=`None`) -- URL of the video.
        - `key`      (=`None`) -- Viewkey of the video (13 or 15 chars).
        - `preload` (=`False`) -- Whether to load the video page in advance.
        
        ---------------------------------------------------------
        Returns a `Video` object.
        '''
        
        assert bool(url) ^ bool(key), 'Must specify exactly one of the URL and the viewkey'
        
        if key is not None:
            url = consts.ROOT + f'view_video.php?viewkey={key}'
        
        return classes.Video(client = self, url = url, preload = preload)
    
    def get_user(self, url: str = None, name: str = None) -> classes.User:
        '''
        #### Attempt to fetch a PornHub user or channel. ####
        -----------------------------------------------------
        
        Arguments:
        - `url`  (=`None`) -- URL of the user page.
        - `name` (=`None`) -- The name of the user.
        
        NOTE - `name` parameter is experimental.
        
        -----------------------------------------------------
        Returns a `User` object.
        '''
        
        log('client', 'Fetching user', name, level = 6)
        
        return classes.User.get(self, url, name)
    
    def search(self, query: str) -> classes.VideoIterator:
        '''
        #### Search for videos on PornHub servers. ####
        -----------------------------------------------
        
        Arguments:
        - `query` -- Sentence to send to the servers.
        
        -----------------------------------------------
        Returns a `VideoIterator` object.
        '''
        
        log('client', 'Opening new search query:', query, level = 6)
        url = consts.ROOT + 'video/search?search=' + query
        return classes.VideoIterator(self, url)

# EOF
