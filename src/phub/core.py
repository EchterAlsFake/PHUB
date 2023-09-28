'''
PHUB core module.
'''

import time
import logging
import requests

from . import utils
from . import consts
from . import errors
from . import locals

from .objects import (
    Query,
    JQuery,
    HQuery,
    MQuery,
    Video,
    User,
    Account,
    Param,
    NO_PARAM
)

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
            proxies (dict): Dictionnary of proxies for the requests.
            login   (bool): Wether to automatically login after initialisation.
        '''
        
        logger.debug('Initialised new Client %s', self)
        
        # Initialise session
        self.session = requests.Session()
        
        # Bypass age disclaimer
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        self.session.cookies.set('accessAgeDisclaimerUK', '1')
        self.session.cookies.set('accessPH', '1')
        self.session.cookies.set('age_verified', '1')

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
    
    def call(self,
             func: str,
             method: str = 'GET',
             data: dict = None,
             headers: dict = {},
             timeout: float = 30,
             throw: bool = True) -> requests.Response:
        '''
        Send a request.
        
        Args:
            func      (str): URL or PH function to call.
            method    (str): Request method.
            data     (dict): Optional data to send to the server.
            headers  (dict): Request optional headers.
            timeout (float): Request maximum response time.
            throw    (bool): Wether to raise an error when a request explicitely fails.
        
        Returns:
            requests.Response: The fetched response.
        '''
        
        logger.info('Making call %s', func)
        
        # Delay
        if self.start_delay:
            time.sleep(self.delay)
        else:
            self.start_delay = True

        url = func if 'http' in func else utils.concat(consts.HOST, func)
        
        # Send request
        response = self.session.request(
            method = method,
            url = url,
            headers = consts.HEADERS | headers | self.language,
            data = data,
            timeout = timeout,
            proxies = self.proxies
        )
        
        if throw: response.raise_for_status()
        return response
    
    def login(self,
              force: bool = False,
              throw: bool = True) -> bool:
        '''
        Attempt to log in.
        
        Args:
            force (bool): Wether to force the login (used to reconnect).
            throw (bool): Wether to raise an error if this fails.
        
        Returns:
            bool: Wether the login was successfull.
        '''
        
        logger.debug('Attempting login')
        
        if not force and self.logged:
            logger.error('Client is already logged in')
            raise errors.ClientAlreadyLogged()
    
        # Get token
        page = self.call('').text
        token = consts.re.get_token(page)
        
        # Send credentials
        payload = consts.LOGIN_PAYLOAD | self.credentials | {'token': token}
        response = self.call('front/authenticate', method = 'POST', data = payload)
        
        # Parse response
        data = response.json()
        success = int(data.get('success'))
        message = data.get('message')
        
        if throw and not success:
            logger.error('Login failed: Received error: %s', message)
            raise errors.LoginFailed(message)
        
        # Update account data
        self.account.connect(data)
        self.logged = bool(success)
        return self.logged
    
    def get(self, video: str) -> Video:
        '''
        Fetch a Pornhub video.
        
        Args:
            video (str): Video full URL, partial URL or viewkey.
        
        Returns:
            Video: The corresponding video object.
        '''
        
        logger.debug('Fetching video at', video)
        
        if 'http' in video:
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
            User: The corresponging user object.
        '''
        
        logger.debug('Fetching user %s', user)
        
        if '/' in user and not 'http' in user:    
            raise NotImplementedError('User partial URL are not implemented.')
        
        return User.get(self, user)

    def search(self,
               query: str,
               param: locals.constant = NO_PARAM,
               feature = JQuery) -> Query:
        '''
        Performs searching on Pornhub.
        
        Args:
            query (str): The query to search.
            param (Param): Filters parameter.
            feature (Query): Query to use for parsing.
        
        Returns:
            Query: Initialised query.
        '''
        
        # Assert param type
        assert isinstance(param, Param)
        logger.info('Opening search query for `%s`', query)
        
        # Assert sorting is compatible
        if (not (locals._allowed_sort_types in param)
            and locals._sort_period_types in param):
            
            raise errors.InvalidSortParam('Sort parameter not allowed')
        
        func = 'video/search' if feature is HQuery else 'search'
        return feature(self, func, Param('search', query) | param)

    def search_user(self,
                    username: str = None,
                    param: Param = NO_PARAM,
                    ) -> MQuery:
        '''
        Search for users in the community.
        
        Args:
            username (str): The menber username.
            param (Param): Filters parameter.
        
        Returns:
            MQuery: Initialised query.
        
        TODO
        - country: str = None,            # &country=AX
        - city: str = None,               # &city=Paris
        - age: tuple[int, int] = (0, 0),  # &age1=0&age2=0
        '''
        
        return MQuery(self, 'user/search', Param('username', username) | param)

# EOFm