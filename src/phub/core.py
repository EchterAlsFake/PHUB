'''
PHUB core module.
'''

import time
import logging

import requests
from typing import Iterable
from functools import cached_property

from . import utils
from . import consts
from . import errors
from . import literals

from .modules import parser

from .objects import (Video, User,
                      Account, Query, queries, Playlist)

logger = logging.getLogger(__name__)

class Client:
    '''
    Represents a client capable of handling requests
    with Pornhub.
    '''
    
    def __init__(self,
                 email: str = None,
                 password: str = None,
                 *,
                 language: literals.language = 'en,en-US',
                 delay: int | float = 0,
                 proxies: dict = None,
                 login: bool = True) -> None:
        '''
        Initialises a new client.
        
        Args:
            email (str): Account email address.
            password (str): Account password.
            language (str): Client language (fr, en, ru, etc.)
            delay (int | float): Minimum delay between requests.
            proxies (dict): Dictionary of proxies for the requests.
            login (bool): Whether to directly log in after initialization.
        
        Raises:
            LoginFailed: If Pornhub refuses the authentification.
                The reason will be passed as the error body.
        '''
        
        logger.debug('Initialised new Client %s', self)
        
        # Initialise session
        self.reset()
        
        self.proxies = proxies
        self.language = {'Accept-Language': language}
        self.credentials = {'email': email,
                            'password': password}
        
        self.delay = delay
        self.start_delay = False
        self.last_request_time = None
        
        # Connect account
        self.logged = False
        self.account = Account(self)
        logger.debug('Connected account to client %s', self.account)
        
        # Automatic login
        if login and self.account:
            self.login()
    
    def reset(self) -> None:
        '''
        Reset the client requests session.
        This is useful if you are keeping the client running
        for a long time and can help with Pornhub rate limit.
        '''
        
        # Initialise session
        self.session = requests.Session()
        self._clear_granted_token()
        
        # Insert cookies
        self.session.cookies.update(consts.COOKIES)

    def call(self,
             func: str,
             method: str = 'GET',
             data: dict = None,
             headers: dict = {},
             timeout: float = consts.CALL_TIMEOUT,
             throw: bool = True,
             silent: bool = False) -> requests.Response:
        '''
        Used internally to send a request or an API call.

        Args:
            func (str): URL or PH function to fetch or call.
            method (str): Request method (GET, POST, PUT, ...).
            data (dict): Optional data to send to the server.
            headers (dict): Additional request headers.
            timeout (float): Request maximum response time.
            throw (bool): Whether to raise an error when a request explicitly fails.
            silent (bool): Whether to supress this call from logs.

        Returns:
            Response: The fetched response.
        
        Raises:
            ConnectionError: If the request was blocked by Pornhub.
            HTTPError: If the request failed, for any reason.
        '''

        logger.log(logging.DEBUG if silent else logging.INFO, 'Fetching %s', func or '/')

        # Delay mechanism
        if self.last_request_time:
            elapsed_time = time.time() - self.last_request_time
            if elapsed_time < self.delay:
                time.sleep(self.delay - elapsed_time)

        self.last_request_time = time.time()  # Update the time of the last request

        url = func if 'http' in func else utils.concat(consts.HOST, func)

        for i in range(consts.MAX_CALL_RETRIES):
            try:
                response = self.session.request(
                    method = method,
                    url = url,
                    headers = headers,
                    data = data,
                    timeout = timeout,
                )

                # Silent 429 errors
                if b'429</title>' in response.content:
                    raise ConnectionError('Pornhub raised error 429: too many requests')

                # Attempt to resolve the challenge if needed
                if challenge := consts.re.get_challenge(response.text, False):
                    logger.info('Challenge found, attempting to resolve')
                    parser.challenge(self, *challenge)
                    
                    logger.info(f"Sleeping for {consts.CHALLENGE_TIMEOUT} seconds")
                    time.sleep(consts.CHALLENGE_TIMEOUT)
                    continue  # Reload page

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
            
        Raises:
            ClientAlreadyLogged: If ``force`` was False and client was already logged.
            LoginFailed: If the login failed, for a reason passed in the error body.
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
        Get a Pornhub video.
        
        Args:
            video (str | Video): Video URL or viewkey.
        
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

    def get_user(self, user: str | User) -> User:
        '''
        Get a Pornhub user.
        
        Args:
            user (str | User): user URL or name.
        
        Returns:
            User: The corresponding user object.
        '''
        
        if isinstance(user, User):
            user = user.url
        
        logger.debug('Fetching user %s', user)
        return User.get(self, user)

    def search_hubtraffic(self,
               query: str,
               *,
               category: literals.category = None,
               tags: str | list[str] = None,
               sort: literals.ht_sort = None,
               period: literals.ht_period = None) -> Query:
        '''
        Perform searching on Pornhub using the HubTraffic API.
        It is condidered to be much faster but has less filters.
        
        Args:
            query (str): The query to search.
            category (str): A category the video is in.
            sort (str): Sorting type.
            period (str): When using sort, specify the search period.
        
        Returns:
            Query: Initialised query response.
        
        Raises:
            AssertionError: If one or more filters don't match their literals.
        '''
        
        literals.ass('category', category, literals.category)
        literals.ass('sort'    , sort    , literals.ht_sort)
        literals.ass('period'  , period  , literals.ht_period)
    
        return queries.JSONQuery(
            client = self,
            func = 'search',
            args = {
                'search': query,
                'category': category,
                'tags[]': literals._craft_list(tags),
                'ordering': literals.map.ht_sort.get(sort),
                'period': literals.map.ht_period.get(period),
            },
            query_repr = query
        )
    
    def search(self,
               query: str,
               *,
               production: literals.production = None,
               category: literals.category = None,
               exclude_category: literals.category | Iterable[literals.category] = None,
               hd: bool = None,
               sort: literals.sort = None,
               period: literals.period = None) -> Query:
        '''
        Performs searching on Pornhub.
        
        Args:
            query (str): The query to search.
            production (str): Production type.
            category (str): A category the video is in. 
            exclude_category (str | list): One or more categories to exclude.
            hd (bool): Whether to search only HD videos.
            sort (str): Sorting type.
            period (str): When using sort, specify the search period.
        
        Returns:
            Query: Initialised query.
        
        Raises:
            AssertioneError: If the query is empty.
            AssertioneError: If one or more filters don't match their literals.
        '''
        
        query = query.strip()
        
        assert query, 'Query must be a non-empty string'
        
        literals.ass('production'      , production      , literals.production)
        literals.ass('category'        , category        , literals.category  )
        literals.ass('exclude_category', exclude_category, literals.category  )
        literals.ass('sort'            , sort            , literals.sort      )
        literals.ass('period'          , period          , literals.period    )
        
        return queries.VideoQuery(
            client = self,
            func = 'video/search',
            args = {
                'search': query,
                'p': production,
                'filter_category': literals.map.category.get(category),
                'exclude_category': literals._craft_list(exclude_category),
                'o': literals.map.sort.get(sort),
                't': literals.map.period.get(period),
                'hd': literals._craft_boolean(hd)
            },
            query_repr = query
        )
    
    def get_playlist(self, playlist: str | int | Playlist) -> Playlist:
        '''
        Get a Pornhub playlist.

        Args:
            playlist (str | int | Playlist): The playlist url or id

        Returns:
            Playlist: The corresponding playlist object.
        
        Raises:
            TypeError: If the playlist argument is invalid.
        '''
        
        if not isinstance(playlist, str | int | Playlist):
            raise TypeError(f'Invalid type: {type(playlist)} should be str, int or Playlist.')
        
        if isinstance(playlist, Playlist):
            playlist = playlist.url
        
        if isinstance(playlist, str) and 'playlist' in playlist:
            playlist = playlist.split('/')[-1]

        return Playlist(self, playlist)

    def search_user(self,
                    username: str = None,                     country: str = None,
                    city: str = None,                         min_age: int = None,
                    max_age: int = None,                      gender: literals.gender = None,
                    orientation: literals.orientation = None, offers: literals.offers = None,
                    relation: literals.relation = None,       sort: literals.sort_user = None,
                    is_online: bool = None,                   is_model: bool = None,
                    is_staff: bool = None,                    has_avatar: bool = None,
                    has_videos: bool = None,                  has_photos: bool = None,
                    has_playlists: bool = None) -> queries.UserQuery:
        '''
        Search for users in the community.
        
        Args:
            username (str): Filters users with a name query.
            country (str): Filter users with a country.
            city (str): Filters users with a city.
            min_age (int): Filters users with a minimal age.
            max_age (int): Filters users with a maximal age.
            gender (gender): Filters users with a gender.
            orientation (orientation): Filters users with an orientation.
            offers (offers): Filters users with what content they do on their channel.
            relation (relation): Filters users with their relation.
            sort (sort_user): Response sort type.
            is_online (bool): Get only online or offline users.
            is_model (bool): Get only model users.
            is_staff (bool): Get only Pornhub staff members.
            has_avatar (bool): Get only users with a custom avatar.
            has_videos (bool): Get only users that have posted videos.
            has_photos (bool): Get only users that have posted photos.
            has_playlists (bool): Get only users that have posted playlists.
        
        Returns:
            UserQuery: Initialised query.
        '''
        
        return queries.UserQuery(
            client = self,
            func = 'user/search',
            args = {
                'o': sort,
                'username': username,
                'country': country,
                'city': city,
                'age1': min_age,
                'age2': max_age,
                'gender': literals.map.gender.get(gender),
                'orientation': literals.map.orientation.get(orientation),
                'offers': literals.map.offers.get(offers),
                'relation': literals.map.relation.get(relation),
                'online': literals._craft_boolean(is_online),
                'isPornhubModel': literals._craft_boolean(is_model),
                'staff': literals._craft_boolean(is_staff),
                'avatar': literals._craft_boolean(has_avatar),
                'vidos': literals._craft_boolean(has_videos),
                'photos': literals._craft_boolean(has_photos),
                'playlists': literals._craft_boolean(has_playlists),
            }
        )

    def _clear_granted_token(self) -> None:
        '''
        Removes the current granted token stored, if any.
        '''
        
        if '_granted_token' in self.__dict__:
            del self._granted_token

    @cached_property
    def _granted_token(self) -> str:
        '''
        Get a granted token for the account. Used internally
        for making API calls.
        
        Raises:
            AssertionError: If the client is not logged in
        '''
        
        assert self.logged, 'Client must be logged in'
        page = self.call('').text
        return consts.re.get_token(page)

# EOF
