'''
Core module of the PHUB package.
'''

from __future__ import annotations
from typing import Self, Callable

import requests

from phub import utils
from phub import consts
from phub import classes


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
    
    def __init__(self, client: Client) -> None:
        '''
        Generate a new Account object.
        '''
        
        self.client = client
        self.name = self.client.creds['username']
        
        # Create partials
        self.liked = self._partial_playlist(f'users/{self.name}/videos/favorites', 'liked')
        self.watched = self._partial_playlist(f'users/{self.name}/videos/recent', 'watched')
        self.recommended = self._partial_playlist('recommended', 'recommended')
    
    def __repr__(self) -> str:
        return f'<phub.core.Account name={self.name}>'
    
    def _partial_playlist(self, path: str, name: str) -> Callable[[], classes.VideoIterator]:
        '''
        Create a partial property for a specific video playlist.
        '''
        
        def func() -> classes.VideoIterator:
            f'''Get the {name} videos of the account.'''
            return classes.VideoIterator(self.client, consts.ROOT + path)

        return func


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
    
    def __repr__(self) -> str:
        status = 'anonymous', 'connect (' + ('not ', '')[self.logged] + 'logged)'
        return f'<phub.Client {status[self._intents_to_login]}>'
    
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
        
        response = self.session.request(
            method = method,
            url = url,
            headers = consts.HEADERS | headers,
            data = data
        )
        
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
        
        # Extract token
        home = self._call('GET', '/').text
        token = consts.regexes.extract_token(home)
        
        # Send credentials
        payload = consts.LOGIN_PAYLOAD | self.creds | {'token': token}
        response = self._call('POST', 'front/authenticate', data = payload)
        success = int(response.json()['success'])
        
        # Throw error
        if throw and not success:
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
        
        return classes.User.get(self, name)
    
    def search(self, query: str) -> classes.VideoIterator:
        '''
        Make a research for videos on PornHub servers.
        '''
        
        url = consts.ROOT + 'video/search?search=' + query
        return classes.VideoIterator(self.client, url)

# EOF