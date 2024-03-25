"""
PHUB core module.

WARNING - THIS CODE IS AUTOMATICALLY GENERATED. UNSTABILITY MAY OCCUR.
FOR ADVANCED DOSCTRINGS, COMMENTS AND TYPE HINTS, PLEASE USE THE DEFAULT BRANCH.
"""
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
from .objects import Video, User, Account, Query, queries, Playlist
logger = logging.getLogger(__name__)


class Client:
    """
    Represents a client capable of handling requests
    with Pornhub.
    """

    def __init__(self, username=None, password=None, *, language='en,en-US', delay=0, proxies=None, login=True):
        """
        Initialise a new client.

        Args:
            username (str): Optional account username/address to connect to.
            password (str): Optional account password to connect to.
            language (str): Language locale (fr, en, ru, etc.)
            delay  (float): Minimum delay between requests.
            proxies (dict): Dictionary of proxies for the requests.
            login   (bool): Whether to automatically log in after initialization.
        """
        logger.debug('Initialised new Client %s', self)
        self.reset()
        self.proxies = proxies
        self.language = {'Accept-Language': language}
        self.credentials = {'username': username, 'password': password}
        self.delay = delay
        self.start_delay = False
        self.logged = False
        self.account = Account(self)
        logger.debug('Connected account to client %s', self.account)
        if login and self.account:
            logger.debug('Automatic login triggered')
            self.login()

    def reset(self):
        """
        Reset the client requests session.
        """
        self.session = requests.Session()
        self._clear_granted_token()
        self.session.cookies.update(consts.COOKIES)

    def call(self, func, method='GET', data=None, headers={}, timeout=consts.CALL_TIMEOUT, throw=True, silent=False):
        """
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
        """
        logger.log(logging.DEBUG if silent else logging.INFO,
                   'Making call %s', func or '/')
        if self.start_delay:
            time.sleep(self.delay)
        else:
            self.start_delay = True
        url = func if 'http' in func else utils.concat(consts.HOST, func)
        for i in range(consts.MAX_CALL_RETRIES):
            try:
                response = self.session.request(method=method, url=url, headers=consts.HEADERS |
                                                headers | self.language, data=data, timeout=timeout, proxies=self.proxies)
                if b'429</title>' in response.content:
                    raise ConnectionError(
                        'Pornhub raised error 429: too many requests')
                if consts.re.get_challenge(response.text, False):
                    logger.info(
                        '\n\nChallenge found, attempting to resolve\n\n')
                    parser.challenge(
                        self, *consts.re.get_challenge(response.text, False))
                    logging.info(
                        f'Sleeping for {consts.CHALLENGE_TIMEOUT} seconds')
                    time.sleep(consts.CHALLENGE_TIMEOUT)
                    continue
                break
            except Exception as err:
                logger.log(logging.DEBUG if silent else logging.WARNING,
                           f'Call failed: {repr(err)}. Retrying (attempt {i + 1}/{consts.MAX_CALL_RETRIES})')
                time.sleep(consts.MAX_CALL_TIMEOUT)
                continue
        else:
            raise ConnectionError(
                f'Call failed after {i + 1} retries. Aborting.')
        if throw:
            response.raise_for_status()
        return response

    def login(self, force=False, throw=True):
        """
        Attempt to log in.

        Args:
            force (bool): Whether to force the login (used to reconnect).
            throw (bool): Whether to raise an error if this fails.

        Returns:
            bool: Whether the login was successful.
        """
        logger.debug('Attempting login')
        if not force and self.logged:
            logger.error('Client is already logged in')
            raise errors.ClientAlreadyLogged()
        page = self.call('').text
        base_token = consts.re.get_token(page)
        payload = consts.LOGIN_PAYLOAD | self.credentials | {
            'token': base_token}
        response = self.call('front/authenticate', method='POST', data=payload)
        data = response.json()
        success = int(data.get('success'))
        message = data.get('message')
        if throw and (not success):
            logger.error('Login failed: Received error: %s', message)
            raise errors.LoginFailed(message)
        self._clear_granted_token()
        self.account.connect(data)
        self.logged = bool(success)
        return self.logged

    def get(self, video):
        """
        Fetch a Pornhub video.

        Args:
            video (str): Video full URL, partial URL or viewkey.

        Returns:
            Video: The corresponding video object.
        """
        logger.debug('Fetching video at', video)
        if isinstance(video, Video):
            url = video.url
        elif 'http' in video:
            url = video
        else:
            if 'key=' in video:
                key = video.split('key=')[1]
            else:
                key = str(video)
            url = utils.concat(consts.HOST, 'view_video.php?viewkey=' + key)
        return Video(self, url)

    def get_user(self, user):
        """
        Get a specific user.

        Args:
            user (str): user URL or name.

        Returns:
            User: The corresponding user object.
        """
        if isinstance(user, User):
            user = user.url
        logger.debug('Fetching user %s', user)
        return User.get(self, user)

    def search_hubtraffic(self, query, *, category=None, tags=None, sort=None, period=None):
        """
        Perform searching on Pornhub using the HubTraffic API.
        It is condidered to be much faster but has less filters.

        Args:
            query    (str): The query to search.
            category (str): A category the video is in. 
            sort     (str): Sorting type.
            period   (str): When using sort, specify the search period.

        Returns:
            Query: Initialised query.
        """
        literals.ass('category', category, literals.category)
        literals.ass('sort', sort, literals.ht_sort)
        literals.ass('period', period, literals.ht_period)
        return queries.JSONQuery(client=self, func='search', args={'search': query, 'category': category, 'tags[]': literals._craft_list(tags), 'ordering': literals.map.ht_sort.get(sort), 'period': literals.map.ht_period.get(period)}, query_repr=query)

    def search(self, query, *, production=None, category=None, exclude_category=None, hd=None, sort=None, period=None):
        """
        Performs searching on Pornhub.

        Args:
            query                   (str): The query to search.
            production              (str): Production type.
            category                (str): A category the video is in. 
            exclude_category (str | list): One or more categories to exclude.
            hd                     (bool): Whether to search only HD videos.
            sort                    (str): Sorting type.
            period                  (str): When using sort, specify the search period.

        Returns:
            Query: Initialised query.
        """
        query = query.strip()
        assert query, 'Query must be a non-empty string'
        literals.ass('production', production, literals.production)
        literals.ass('category', category, literals.category)
        literals.ass('exclude_category', exclude_category, literals.category)
        literals.ass('sort', sort, literals.sort)
        literals.ass('period', period, literals.period)
        return queries.VideoQuery(client=self, func='video/search', args={'search': query, 'p': production, 'filter_category': literals.map.category.get(category), 'exclude_category': literals._craft_list(exclude_category), 'o': literals.map.sort.get(sort), 't': literals.map.period.get(period), 'hd': literals._craft_boolean(hd)}, query_repr=query)

    def get_playlist(self, pl):
        """
        Initializes a Playlist object.

        Args:
            pl (str | int | Playlist): The playlist url or id

        Returns:
            Playlist object
        """
        assert isinstance(pl, object), 'Invalid type'
        if isinstance(pl, Playlist):
            pl = pl.url
        if isinstance(pl, str) and 'playlist' in pl:
            pl = pl.split('/')[-1]
        return Playlist(self, pl)

    def search_user(self, username=None, country=None, city=None, min_age=None, max_age=None, gender=None, orientation=None, offers=None, relation=None, sort=None, is_online=None, is_model=None, is_staff=None, has_avatar=None, has_videos=None, has_photos=None, has_playlists=None):
        """
        Search for users in the community.

        Returns:
            UserQuery: Initialised query.
        """
        return queries.UserQuery(client=self, func='user/search', args={'o': sort, 'username': username, 'country': country, 'city': city, 'age1': min_age, 'age2': max_age, 'gender': literals.map.gender.get(gender), 'orientation': literals.map.orientation.get(orientation), 'offers': literals.map.offers.get(offers), 'relation': literals.map.relation.get(relation), 'online': literals._craft_boolean(is_online), 'isPornhubModel': literals._craft_boolean(is_model), 'staff': literals._craft_boolean(is_staff), 'avatar': literals._craft_boolean(has_avatar), 'vidos': literals._craft_boolean(has_videos), 'photos': literals._craft_boolean(has_photos), 'playlists': literals._craft_boolean(has_playlists)})

    def _clear_granted_token(self):
        """
        Clear the granted token cache.
        """
        if '_granted_token' in self.__dict__:
            del self._granted_token

    @cached_property
    def _granted_token(self):
        """
        Get a granted token after having
        authentified the account.
        """
        assert self.logged, 'Client must be logged in'
        self._token_controller = True
        page = self.call('').text
        return consts.re.get_token(page)
