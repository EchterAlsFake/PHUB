'''
PHUB core module.
'''

import time
import logging

import requests
from functools import cached_property

from . import utils
from . import consts
from . import errors
from . import locals

from .modules import parser

from .objects import (Param, NO_PARAM, Video, User,
                      Account, Query, queries)

logger = logging.getLogger(__name__)

class Client:
    '''
    Represents a client capable of handling requests
    with Pornhub.
    '''
    
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 *,
                 language: str = 'en,en-US',
                 delay: int = 0,
                 proxies: dict = None,
                 login: bool = True) -> None:
        '''
        Initialise a new client.
        
        Args:
            username (str): Optional account username/address to connect to.
            password (str): Optional account password to connect to.
            language (str): Language locale (fr, en, ru, etc.)
            delay  (float): Minimum delay between requests.
            proxies (dict): Dictionary of proxies for the requests.
            login   (bool): Whether to automatically log in after initialization.
        '''
        
        logger.debug('Initialised new Client %s', self)
        
        # Initialise session
        self.reset()
        
        self.proxies = proxies
        self.language = {'Accept-Language': language}
        self.credentials = {'username': username,
                            'password': password}
        
        self.delay = delay
        self.start_delay = False
        
        # Connect account
        self.logged = False
        self.account = Account(self)
        logger.debug('Connected account to client %s', self.account)
        
        # Automatic login
        if login and self.account:
            logger.debug('Automatic login triggered')
            self.login()
    
    def reset(self) -> None:
        '''
        Reset the client requests session.
        '''
        
        # Initialise session
        self.session = requests.Session()
        self._clear_granted_token()
        
        # Bypass age disclaimer
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        self.session.cookies.set('accessAgeDisclaimerUK', '1')
        self.session.cookies.set('accessPH', '1')
        self.session.cookies.set('age_verified', '1')
    
    def call(self,
             func: str,
             method: str = 'GET',
             data: dict = None,
             headers: dict = {},
             timeout: float = 30,
             throw: bool = True,
             silent: bool = False) -> requests.Response:
        '''
        Send a request.
        
        Args:
            func      (str): URL or PH function to call.
            method    (str): Request method.
            data     (dict): Optional data to send to the server.
            headers  (dict): Request optional headers.
            timeout (float): Request maximum response time.
            throw    (bool): Whether to raise an error when a request explicitly fails.
            silent   (bool): Make the call logging one level deeper.
        
        Returns:
            requests.Response: The fetched response.
        '''
        
        logger.log(logging.DEBUG if silent else logging.INFO, 'Making call %s', func or '/')
        
        # Delay
        if self.start_delay:
            time.sleep(self.delay)
        else:
            self.start_delay = True

        url = func if 'http' in func else utils.concat(consts.HOST, func)
        
        for i in range(consts.MAX_CALL_RETRIES):
            
            try:
                # Send request
                response = self.session.request(
                    method = method,
                    url = url,
                    headers = consts.HEADERS | headers | self.language,
                    data = data,
                    timeout = timeout,
                    proxies = self.proxies
                )
                
                # Silent 429 errors
                if b'429</title>' in response.content:
                    raise ConnectionError('Pornhub raised error 429: too many requests')
                
                # Attempt to resolve the challenge if needed
                if challenge := consts.re.get_challenge(response.text, False):
                    logger.info('\n\nChallenge found, attempting to resolve\n\n')
                    parser.challenge(self, *challenge)
                    continue # Reload page
                
                break
            
            except Exception as err:
                logger.log(logging.DEBUG if silent else logging.WARNING,
                           f'Call failed: {repr(err)}. Retrying (attempt {i + 1}/{consts.MAX_CALL_RETRIES})')
                time.sleep(consts.MAX_CALL_TIMEOUT)
                continue
        
        else:
            raise ConnectionError(f'Call failed after {i + 1} retries. Aborting.')

        if throw: response.raise_for_status()
        return response
    
    def login(self,
              force: bool = False,
              throw: bool = True) -> bool:
        '''
        Attempt to log in.
        
        Args:
            force (bool): Whether to force the login (used to reconnect).
            throw (bool): Whether to raise an error if this fails.
        
        Returns:
            bool: Whether the login was successful.
        '''
        
        logger.debug('Attempting login')
        
        if not force and self.logged:
            logger.error('Client is already logged in')
            raise errors.ClientAlreadyLogged()
    
        # Get token
        page = self.call('').text
        base_token = consts.re.get_token(page)
        
        # Send credentials
        payload = consts.LOGIN_PAYLOAD | self.credentials | {'token': base_token}
        response = self.call('front/authenticate', method = 'POST', data = payload)
        
        # Parse response
        data = response.json()
        success = int(data.get('success'))
        message = data.get('message')
        
        if throw and not success:
            logger.error('Login failed: Received error: %s', message)
            raise errors.LoginFailed(message)
        
        # Reset token
        self._clear_granted_token()
        
        # Update account data
        self.account.connect(data)
        self.logged = bool(success)
        return self.logged
    
    def get(self, video: str | Video) -> Video:
        '''
        Fetch a Pornhub video.
        
        Args:
            video (str): Video full URL, partial URL or viewkey.
        
        Returns:
            Video: The corresponding video object.
        '''
        
        logger.debug('Fetching video at', video)

        if isinstance(video, Video):
            # User might want to re-init a video,
            # or use another client
            url = video.url
        
        elif 'http' in video:
            # Support full URLs
            url = video
        
        else:
            if 'key=' in video:
                # Support partial URLs
                key = video.split('key=')[1]
            
            else:
                # Support key only
                key = str(video)
            
            url = utils.concat(consts.HOST, 'view_video.php?viewkey=' + key)
        
        return Video(self, url)

    def get_user(self, user: str) -> User:
        '''
        Get a specific user.
        
        Args:
            user (str): user URL or name.
        
        Returns:
            User: The corresponding user object.
        '''
        
        logger.debug('Fetching user %s', user)
        return User.get(self, user)

    def search(self,
               query: str,
               param: locals.constant = NO_PARAM,
               use_hubtraffic = True) -> Query:
        '''
        Performs searching on Pornhub.
        
        Args:
            query (str): The query to search.
            param (Param): Filters parameter.
            use_hubtraffic (bool): Whether to use the HubTraffic Pornhub API (faster but less precision).
        
        Returns:
            Query: Initialised query.
        '''
        
        # Assert a param type
        assert isinstance(param, Param)
        logger.info('Opening search query for `%s`', query)
        
        # Assert sorting is compatible
        if (not (locals._allowed_sort_types in param)
            and locals._sort_period_types in param):
            
            raise errors.InvalidSortParam('Sort parameter not allowed')
        
        param_ = Param('search', query) | param
        
        if use_hubtraffic:
            return queries.JSONQuery(self, 'search', param_, query_repr = query)
        
        return queries.VideoQuery(self, 'video/search', param_, query_repr = query)
    
    def search_user(self,
                    username: str = None,
                    country: str = None,
                    city: str = None,
                    age: tuple[int] = None,
                    param: Param = NO_PARAM
                    ) -> queries.UserQuery:
        '''
        Search for users in the community.
        
        Args:
            username (str): The member username.
            country (str): The member **country code** (AF, FR, etc.)
            param (Param): Filters parameter.
        
        Returns:
            MQuery: Initialised query.
        
        '''
        
        params = (param
                  | Param('username', username)
                  | Param('city', city)
                  | Param('country', country))
        
        if age:
            params |= Param('age1', age[0])
            params |= Param('age2', age[1])
        
        return queries.UserQuery(self, 'user/search', params)

    def _clear_granted_token(self) -> None:
        '''
        Clear the granted token cache.
        '''
        
        if '_granted_token' in self.__dict__:
            del self._granted_token

    @cached_property
    def _granted_token(self) -> str:
        '''
        Get a granted token after having
        authentified the account.
        '''
        
        assert self.logged, 'Client must be logged in'
        self._token_controller = True

        page = self.call('').text
        return consts.re.get_token(page)

# EOF
