'''
Core module of the PHUB package.
'''

from __future__ import annotations
from io import TextIOWrapper
from typing import Self, Literal

import json
import requests
from time import sleep
from functools import cached_property

from phub import utils
from phub import consts
from phub import errors
from phub import classes
from phub.utils import log, register_properties

@register_properties
class Account:
    '''
    Represent a Client's account.
    '''
    
    def __new__(cls, client: Client) -> Self:
        '''
        Verify that user has entered credentials.
        Returns None if no account used.
        
        Args:
            client: The client session.
        
        Returns:
            Account: An account if the connection is etablished.
        '''
        
        if client._intents_to_login:
            return object.__new__(cls)
        
        log('accnt', 'Passing account creation')
    
    def __init__(self, client: Client) -> None:
        '''
        Generate a new Account object.
        
        Args:
            client: The client session.
        '''
        
        self.client = client
        self.name = self.client.creds['username']
        
        log('accnt', 'Initialised new account', repr(self))
    
    def __repr__(self) -> str:
        return f'<phub.core.Account name={self.name}>'
    
    def __getattribute__(self, item: str):
        '''
        Verify that the client is logged in.
        '''
        
        obj = object.__getattribute__(self, item)
        
        # Bypass dunder & private methods & attributes
        if item.startswith('_'): return obj
        
        if item in self.__properties__ and not self.client.logged:
            raise errors.NotLoggedIn('Client is not logged in.')
        
        return obj
    
    def refresh(self) -> None:
        '''
        Delete the cache to allow refreshing items of this object.
        '''
        
        # Clear the cache
        log('accnt', 'Clearing cache of', self, level = 4)
        
        for name in self.__properties__:
            if name in self.__dict__:
                delattr(self, name)

    @cached_property
    def recommended(self) -> classes.Query:
        '''
        Get the recommended videos for the user.

        Returns:
            Query: The resulting query object.
        '''
        
        return classes.Query(self.client, consts.ROOT + 'recommended')
    
    @cached_property
    def watched(self) -> classes.Query:
        '''
        Get the history of the user.
        
        Returns:
            Query: The resulting query object.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/recent'
        return classes.Query(self.client, url,
                                     corrector = utils.remove_video_ads)

    @cached_property
    def liked(self) -> classes.Query:
        '''
        Get the favorite videos of the account.
        
        Returns:
            Query: The resulting query object.
        '''
        
        url = consts.ROOT + f'users/{self.name}/videos/favorites'
        return classes.Query(self.client, url,
                                     corrector = utils.remove_video_ads)

    @cached_property
    def feed(self) -> classes.Feed:
        '''
        Get the account feed.

        Returns:
            Feed: The feed object.
        '''
        
        return classes.Feed(self.client)


class Client:
    '''
    Represents a Client capable of interacting with PornHub.
    '''
    
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 session: requests.Session = None,
                 language: str = 'en,en-US',
                 autologin: bool = True,
                 delay: bool = False) -> None:
        '''
        Initialise a new client.
        
        Args:
            username (str): Account to connect to username.
            password (str): Account to connect to password.
            session (request.Session): Recovery requests session.
            language (str): Language of the client session.
            autologin (bool): Whether to login after initialisation.
        '''
        
        # Initialise session
        self.session = session or requests.Session()
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        
        # Account setings
        self.logged = False
        self.creds = {'username': username, 'password': password}
        self._intents_to_login = bool(username)
        self.language = {'Accept-Language': language}
        
        # Delay settings
        self.delay = (0, .5)[delay]
        self._has_called = False
        
        # Connect Account object
        self.account: Account | None = Account(self)
        
        # Autologin
        if autologin and self._intents_to_login:
            self.login()
        
        log('clien', 'Initialised new client', repr(self))

    def __repr__(self) -> str:
        '''
        Display Client object representation and informations about
        whether the account is connected.
        '''
        
        status = 'anonymous', 'w/account (' + ('not ', '')[self.logged] + 'logged)'
        return f'<phub.Client {status[self._intents_to_login]}>'
    
    def __str__(self) -> str:
        return repr(self)
    
    @classmethod
    def from_file(cls, data: str | dict | TextIOWrapper) -> Self:
        '''
        Generate a new client from credentials.
        
        Args:
            data (str | dict | TextIO): Dictionnary, JSON file or JSON string to get username and password from.
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
                
                log('clien', 'Initialising client from', type(data), level = 7)
                return cls(**data)
            
            raise KeyError('Data must have username and password keys.')
        
        raise TypeError('Invalid type for data:', type(data))
    
    def _call(self,
              method: str,
              func: str,
              headers = {},
              data: dict = None,
              simple_url: bool = True,
              throw: bool = True) -> requests.Response:
        '''
        Handle sending and receiving custom requests from PornHub servers.
        
        Args:
            method (str): Request method (GET, POST, PUT, etc.).
            func (str): Name and arguments of the PornHub function.
            headers (dict): Optional headers to add.
            data (dict): Optional payload to send.
            simple_url (bool): Whether to consider `func` as a simple Pornhub.
            throw (bool): Whether to handle HTTP related errors.
        
        Returns:
            requests.Response: The response to that request.
        '''
        
        # Delay if needed
        if self._has_called: sleep(self.delay)
        
        url = consts.ROOT + utils.slash(func, '**') \
              if simple_url else func
        
        log('clien', f'Sending request at {utils.shortify(func, 120)}', level = 6)
        
        response = self.session.request(
            method = method,
            url = url,
            headers = consts.HEADERS | headers | self.language,
            data = data
        )
        
        log('clien', 'Request passed with status', response.status_code, level = 6)
        
        if throw and response.status_code == 429:
            raise errors.TooManyRequests('Too many requests.')

        if throw and not response.ok:
            raise ConnectionError(f'Request `{func}` failed.')
        
        self._has_called = True
        return response
    
    def login(self, force: bool = False, throw: bool = True) -> bool:
        '''
        Attempt to login to PornHub.
        
        Args:
            throw (bool): Raise errors in case of HTTP errors.
        
        Returns:
            bool: whether the operation was successful.
        '''
        
        if not force and self.logged:
            raise errors.AlreadyLoggedIn('Account already connected.')
        
        log('client', 'Attempting loggin...', level = 6)
        
        # Extract token
        home = self._call('GET', '/').text
        token = consts.regexes.extract_token(home)
        log('clien', 'Extracted token', token, level = 5)
        
        # Send credentials
        log('clien', 'Sending payload', level = 5)
        payload = consts.LOGIN_PAYLOAD | self.creds | {'token': token}
        
        response = self._call('POST', 'front/authenticate', data = payload)
        success = int(response.json()['success'])
        
        if success:
            log('clien', 'Login successful!', level = 6)
        
        else:
            log('clien', 'Login failed', level = 2)
            
            # Throw error
            if throw:
                raise errors.LogginFailed('Login failed. Check credentials.')
        
        self.logged = success
        return success

    def get(self, url: str = None, key: str = None, preload: bool = True) -> classes.Video:
        '''
        Get a specific video using an URL or a viewkey.
        
        Args:
            url (str): URL of the video.
            key (str): Viewkey of the video (13 or 15 chars).
            preload (bool): Whether to load the video page in advance.
        
        Returns:
            Video: The fetched video object.
        '''
        
        assert bool(url) ^ bool(key), 'Must specify exactly one of the URL and the viewkey'
        
        if key is not None:
            url = consts.ROOT + f'view_video.php?viewkey={key}'
        
        return classes.Video(client = self, url = url, preload = preload)
    
    def get_user(self, url: str = None, name: str = None) -> classes.User:
        '''
        Attempt to fetch a PornHub user or channel.
        
        Args:
        url (str): URL of the user page.
        name (str): The name of the user (experimental).
        
        Returns:
            User: The fetched user object.
        '''
        
        log('clien', 'Fetching user', name, level = 6)
        
        return classes.User.get(self, url, name)
    
    def search(self,
               query: str,
               production: Literal['professional', 'homemade'] | None = None,
               duration: tuple[int] | None = None,
               hd: bool = False,
               category: utils.Category = None,
               exclude_category: utils.Category = None,
               sort: Literal['most relevant', 'most recent',
                             'most viewed', 'top rated', 'longest'] = None,
               time: Literal['day', 'week', 'month', 'year'] | None = None
               ) -> classes.Query:
        '''
        Search for videos on PornHub servers.
        
        Args:
            query (str): Sentence to send to the server.
            production (str): The production type, professional or homemade (both by default).
            duration (tuple[int]): Video duration boundaries.
            hd (bool): Wether to get only HD quality videos.
            category (utils.Category): The video category to search in.
            exclude_category (utils.Category): The video category(ies) to exclude from searching.
            sort (str): How to sort videos (most relevant by default).
            time (str): Video release approximation (does not work when sorting most relevant).
        
        Returns:
            Query: The fetched query object.
        '''
        
        url = consts.ROOT + 'video/search?search=' + query
        sort = consts.SEARCH_SORT_TRANSLATION[sort]
        
        # Add filters
        if hd:               url += '&hd=1'
        if production:       url += f'&p={production}'
        if duration:         url += '&min_duration={}&max_duration={}'.format(*duration) # TODO
        if category:         url += '&filter_category=' + str(category)
        if exclude_category: url += '&exclude_category=' + str(exclude_category)
        if sort:             url += f'&o={sort}'
        if time and sort:    url += f'&t=' + time[0]
        
        log('clien', 'Opening new search query:', url, level = 6)
        return classes.Query(self, url, utils.remove_video_ads)

# EOF
