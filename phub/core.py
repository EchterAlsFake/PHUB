import time
import requests

from . import utils
from . import consts
from . import errors
from . import objects


class Client:
    
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 *,
                 language: str = 'en,en-US',
                 delay: int = 0,
                 login: bool = True) -> None:
        '''
        Initialise a new client.
        '''
        
        # Initialise session
        self.session = requests.Session()
        
        # Bypass age disclaimer
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        self.session.cookies.set('accessAgeDisclaimerUK', '1')
        self.session.cookies.set('accessPH', '1')
        self.session.cookies.set('age_verified', '1')

        self.language = {'Accept-Language': language}
        self.credentials = {'username': username,
                            'password': password}
        
        self.delay = delay
        self.start_delay = False
        
        # Connect account
        self.logged = False
        self.account = objects.Account(self)
        
        # Automatic login
        if login and self.account: self.login()
    
    def call(self,
             func: str,
             method: str = 'GET',
             data: dict = None,
             headers: dict = {},
             throw: bool = True) -> requests.Response:
        '''
        Send a request. 
        '''
        
        print('CALL =>', func)
        
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
            data = data
        )
        
        if throw: response.raise_for_status()
        return response
    
    def login(self,
              force: bool = False,
              throw: bool = True) -> bool:
        '''
        Attempt to login.
        '''
        
        if not force and self.logged:
            raise errors.ClientAlreadyLogged()
    
        # Get token
        page = self.call('').text
        token = consts.re.get_token(page)
        
        # Send credentials
        payload = consts.LOGIN_PAYLOAD | self.credentials | {'token': token}
        response = self.call('front/authenticate', method = 'POST',
                             data = payload)
        
        data = response.json()
        
        success = int(data['success'])
        
        if throw and not success:
            raise errors.LoginFailed(data.get('message'))
        
        # Update account data
        self.account.connect(data)
        self.logged = bool(success)
        return self.logged
    
    def get(self, video: str) -> objects.Video:
        '''
        Fetch a Pornhub video.
        '''
        
        url = video if video.startswith('http') \
              else utils.concat(consts.HOST, 'view_video.php?viewkey=' + video)
        
        return objects.Video(self, url)

# EOF