import time
import logging
import requests

from . import utils
from . import consts
from . import errors

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
        '''
        
        logger.debug('Fetching video at', video)
        
        url = video if video.startswith('http') \
              else utils.concat(consts.HOST, 'view_video.php?viewkey=' + video)
        
        return Video(self, url)

    def get_user(self, user: str) -> User:
        '''
        Get a specific user.
        '''

        logger.debug('Fetching user %s', user)
        return User.get(self, user)

    def search_user(self,
                    username: str = None,
                    country: str = None,
                    city: str = None,
                    gender: str = None,
                    orientation: str = None,
                    filter: Param = NO_PARAM) -> HQuery:
        '''
        Search for users in the community.
        '''
        
        # ?username=bonjour
        # &gender=3
        # &orientation=1
        # &relation=1
        # &city=Paris
        # &country=AX
        
        # &o=popular
        # &age1=0
        # &age2=0
        
        args = 'user/search'
        
        return MQuery(self, args + filter.gen())

    def search(self,
               query: str,
               filter: Param = NO_PARAM,
               feature = JQuery) -> Query:
        '''
        Performs research on Pornhub.
        '''
        
        url = 'search'
        key = 'name'
        
        if feature is HQuery:
            key = 'id'
            url = 'video/' + url
        
        args = {'search': query} | filter.gen(key)
        raw = url + utils.urlify(args)
        
        logger.info('Opening search query at %s', raw)
        return feature(client = self, args = raw)

# EOF