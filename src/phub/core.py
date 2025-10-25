'''
PHUB core module.
'''
import re
import time
import logging
import random
import httpx

from functools import cached_property
from typing import Iterable, Union, Optional
from base_api.base import BaseCore, setup_logger
from base_api.modules.config import RuntimeConfig

from . import utils
from . import consts
from . import errors
from . import literals
from .errors import LoginFailed

from .modules import parser

from .objects import (Video, User,
                      Account, Query, queries, Playlist)


class Client:
    '''
    Represents a client capable of handling requests
    with Pornhub.
    '''
    use_webmaster_api = True

    def __init__(self,
                 email: str = None,
                 password: str = None,
                 *,
                 language: literals.language = 'en',
                 login: bool = True,
                 bypass_geo_blocking: bool = False,
                 change_title_language: bool = True,
                 use_webmaster_api: bool = True,
                 core: Optional[BaseCore] = None) -> None:
        '''
        Initialises a new client.
        
        Args:
            email (str): Account email address.
            password (str): Account password.
            language (str): Client language (fr, en, ru, etc.)
            login (bool): Whether to directly log in after initialization.
            bypass_geo_blocking (bool): Whether to bypass geo-blocking.
            change_title_language (bool): Whether to change title language into your language based on the input URL
            use_webmaster_api (bool): Whether to use the webmaster API or HTML content extraction
        Raises:
            LoginFailed: If Pornhub refuses the authentication.
                The reason will be passed as the error body.
        '''

        self.logger = setup_logger(name="PHUB API - [Client]", log_file=None, level=logging.ERROR)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session()
        self.core.session.headers.update(consts.HEADERS)
        self.core.session.cookies.update(consts.HEADERS)
        # Applying PornHub specific cookies and headers to base API
        self.logger.debug('Initialised new Client %s', self)

        # Initialise session
        Client.use_webmaster_api = use_webmaster_api
        self.language = language
        self.change_title_language = change_title_language
        self.bypass_geo_blocking = bypass_geo_blocking

        self.reset()

        self.core.session.headers.update({"Accept-Language": language})
        self.credentials = {'email': email,
                            'password': password}


        # Connect account
        self.logged = False
        self.account = Account(self)
        self.logger.debug('Connected account to client %s', self.account)
        
        # Automatic login
        if login and self.account:
            self.login()

    def enable_logging(self, log_file: str = None, level = None, log_ip=None, log_port=None):
        self.logger = setup_logger(name="PHUB API - [Client]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    def reset(self) -> None:
        '''
        Reset the client requests session.
        This is useful if you are keeping the client running
        for a long time and can help with Pornhub rate limit.
        '''
        self._clear_granted_token()

        if self.bypass_geo_blocking:
            ip = random.choice(consts.GEO_BYPASS_IPs)
            language_code = "fr"

            # Faking the X-Forwarded-For header (Fake IP source)
            self.core.session.headers.update({"X-Forwarded-For": f"{ip}"})
            # Setting the Accept-Language tag to French, because the faked IP comes from france
            self.core.session.headers.update({"Accept-Language": f"{language_code}"})
            # Setting the country code also to french
            self.core.session.headers.update({"CF-IPCountry": f"{language_code}"})
            logging.debug(f"Using faked headers for geo-bypass: {self.core.config.session.headers}")

    def call(self,
             func: str,
             method: str = 'GET',
             data: dict = None,
             headers: dict = None,
             throw: bool = True,
             silent: bool = False,
             get_response = True) -> httpx.Response:
        '''
        Used internally to send a request or an API call.

        Args:
            func (str): URL or PH function to fetch or call.
            method (str): Request method (GET, POST, PUT, ...).
            data (dict): Optional data to send to the server.
            headers (dict): Additional request headers.
            throw (bool): Whether to raise an error when a request explicitly fails.
            silent (bool): Whether to supress this call from logs.

        Returns:
            Response: The fetched response.
        
        Raises:
            ConnectionError: If the request was blocked by Pornhub.
            HTTPError: If the request failed, for any reason.
        '''
        func = utils.fix_url(func)
        self.logger.log(logging.DEBUG if silent else logging.INFO, 'Fetching %s', func or '/')

        if headers:
            self.core.session.headers = headers

        if not self.language == "en":
            host = consts.LANGUAGE_MAPPING.get(self.language)
            logging.debug(f"Changed PornHub root host to: {host}")

        else:
            host = consts.HOST

        url = func if 'http' in func else utils.concat(host, func)
        for i in range(self.core.config.max_retries):
            try:
                response = self.core.fetch(
                    method = method,
                    url = url,
                    data = data,
                    get_response=get_response)

                # Silent 429 errors
                if b'429</title>' in response.content:
                    raise ConnectionError('Pornhub raised error 429: too many requests')

                # Attempt to resolve the challenge if needed
                challenge = consts.re.get_challenge(response.text, False)
                if challenge:
                    self.logger.info('Challenge found, attempting to resolve')
                    parser.challenge(self, *challenge)
                    
                    self.logger.info(f"Sleeping for 1.5 seconds")
                    time.sleep(1.5) # Yes, we need to sleep that amount, otherwise PornHub refuses the challenge.
                    continue  # Reload page

                break

            except Exception as err:
                self.logger.log(logging.DEBUG if silent else logging.WARNING,
                           f'Call failed: {repr(err)}. Retrying (attempt {i + 1}/{self.core.config.max_retries})')
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
        
        self.logger.debug('Attempting login')
        
        if not force and self.logged:
            self.logger.error('Client is already logged in')
            raise errors.ClientAlreadyLogged()
    
        # Get token
        page = self.call('https://www.pornhub.com').text
        try:
            base_token = consts.re.get_token(page)

        except errors.RegexError:
            self.logger.warning("Couldn't get token. Trying alternative method...")
            base_token = re.search(r'data-token="(.*?)"', string=page).group(1)

        # Send credentials
        payload = consts.LOGIN_PAYLOAD | self.credentials | {'token': base_token}
        response = self.call('front/authenticate', method = 'POST', data = payload)
        
        # Parse response
        data = response.json()
        success = int(data.get('success'))
        message = data.get('message')
        
        if throw and not success:
            self.logger.error('Login failed: Received error: %s', message)
            raise errors.LoginFailed(message)
        
        # Reset token
        self._clear_granted_token()
        
        # Update account data
        self.account.connect(data)
        self.logged = bool(success)
        return self.logged
    
    def get(self, video: Union[str, Video]) -> Video:
        '''
        Get a Pornhub video.
        
        Args:
            video (str | Video): Video URL or viewkey.
        
        Returns:
            Video: The corresponding video object.
        '''
        
        self.logger.debug(f'Fetching video at {video}')

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
        
        return Video(self, url, change_title_language=self.change_title_language)

    def get_user(self, user: Union[str, User]) -> User:
        '''
        Get a Pornhub user.
        
        Args:
            user (str | User): user URL or name.
        
        Returns:
            User: The corresponding user object.
        '''
        
        if isinstance(user, User):
            user = user.url
        
        self.logger.debug('Fetching user %s', user)
        return User.get(self, user)

    def search_hubtraffic(self,
               query: str,
               *,
               category: literals.category = None,
               tags: Union[str, list[str]] = None,
               sort: literals.ht_sort = None,
               period: literals.ht_period = None) -> Query:
        '''
        Perform searching on Pornhub using the HubTraffic API.
        It is considered to be much faster but has less filters.
        
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
               exclude_category: Union[literals.category, Iterable[literals.category]] = None,
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
        
        query = query.strip().lower()
        
        assert query, 'Query must be a non-empty string'
        
        literals.ass('production'      , production      , literals.production)
        literals.ass('category'        , category        , literals.category  )
        literals.ass('exclude_category', exclude_category, literals.category  )
        literals.ass('sort'            , sort            , literals.sort      )
        literals.ass('period'          , period          , literals.period    )
        s = f'search "{query}"'
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
            query_repr = s)
    
    def get_playlist(self, playlist: Union[str, int, Playlist]) -> Playlist:
        '''
        Get a Pornhub playlist.

        Args:
            playlist (str | int | Playlist): The playlist url or id

        Returns:
            Playlist: The corresponding playlist object.
        
        Raises:
            TypeError: If the playlist argument is invalid.
        '''
        
        if not isinstance(playlist, (str, int, Playlist)):
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
