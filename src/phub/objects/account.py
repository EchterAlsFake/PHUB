from __future__ import annotations
import logging
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Iterator
from .. import utils
from .. import consts
from . import User, Image
if TYPE_CHECKING:
    from ..core import Client
    from . import Feed, queries, User
logger = logging.getLogger(__name__)


class Account:
    """
    Represents a connected Ponhub account,
    capable of accessing account-only features.
    If the login fails, there will be None.
    """

    def __new__(cls, client):
        """
        Check if the object creation is needed.

        Args:
            client (Client): The client that initialized this.

        Returns:
            Self: The Account object or None, if login is not triggered.
        """
        if all(client.credentials.values()):
            logger.info('Creating new account object')
            return object.__new__(cls)

    def __init__(self, client):
        """
        Initialise a new account object.

        Args:
            client (Client): The client parent.
        """
        self.client = client
        self.name: str = None
        self.avatar: Image = None
        self.is_premium: bool = None
        self.user: User = None
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        logger.info('Account object %s created', self)

    def __repr__(self):
        status = 'logged-out' if self.name is None else f'name={self.name}'
        return f'phub.Account({status})'

    def connect(self, data):
        """
        Update account data once login was successful.

        Args:
            data (dict): Data fetched from the login request.
        """
        self.name = data.get('username')
        self.avatar = Image(self.client, data.get('avatar'), name='avatar')
        self.is_premium = data.get('premium_redirect_cookie') != '0'
        url = consts.HOST + f'/users/{self.name}'
        self.user = User(client=self.client, name=self.name, url=url)
        if not 'users/' in self.user.url:
            logger.error('Invalid user type: %s', url)
            raise NotImplementedError('Non-user account are not supported.')

    def refresh(self, refresh_login=False):
        """
        Delete the object's cache to allow items refreshing.

        Args:
            refresh_login (bool): Whether to also attempt to re-log in.
        """
        logger.info('Refreshing account %s', self)
        if refresh_login:
            logger.info('Forcing login refresh')
            self.client.login(force=True)
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                logger.debug('Deleting key %s', key)
                delattr(self, key)

    def fix_recommendations(self):
        """
        Allow recommandations cookies.
        """
        logger.info('Fixing account recommendations')
        payload = utils.urlify(
            {'token': self.client._granted_token, 'cookie_selection': 3, 'site_id': 1})
        res = self.client.call(
            'user/log_user_cookie_consent' + payload, silent=True)
        assert res.json().get('success')

    @cached_property
    def recommended(self):
        """
        Videos recommended to the account.
        """
        from . import queries
        self.fix_recommendations()
        return queries.VideoQuery(self.client, 'recommended')

    @cached_property
    def watched(self):
        """
        Account video history.
        """
        from . import queries
        return queries.VideoQuery(self.client, f'users/{self.name}/videos/recent')

    @cached_property
    def liked(self):
        """
        Videos liked by the account.
        """
        from . import queries
        return queries.VideoQuery(self.client, f'users/{self.name}/videos/favorites')

    @cached_property
    def subscriptions(self):
        """
        Get the account subscriptions.
        """
        page = self.client.call(f'users/{self.name}/subscriptions')
        for url, avatar in consts.re.get_users(page.text):
            obj = User.get(self.client, utils.concat(consts.HOST, url))
            obj._cached_avatar_url = avatar
            yield obj

    @cached_property
    def feed(self):
        """
        The account feed.
        """
        from . import Feed
        return Feed(self.client)

    def dictify(self, keys='all', recursive=False):
        """
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: Dict version of the object.
        """
        return utils.dictify(self, keys, ['name', 'avatar', 'is_premium', 'user'], recursive)
