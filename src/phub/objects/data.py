from __future__ import annotations
from functools import cached_property
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal
from .. import utils
from .. import consts
if TYPE_CHECKING:
    from .. import Client
    from . import User
    from bs4 import BeautifulSoup as Soup


@dataclass
class Tag:
    """
    Video Tag representation.
    """
    name: object
    count: object = field(default=None, repr=False)

    def __eq__(self, __value):
        assert isinstance(__value, Tag)
        return self.name == __value.name

    def dictify(self, keys='all', recursive=False):
        """
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: A dict version of the object.
        """
        return utils.dictify(self, keys, ['name', 'count'], recursive)


@dataclass
class Like:
    """
    Represents video likes and their ratings.
    """
    up: object
    down: object
    ratings: object = field(repr=False)

    def dictify(self, keys='all', recursive=False):
        """
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: A dict version of the object.
        """
        return utils.dictify(self, keys, ['up', 'down', 'ratings'], recursive)


@dataclass
class FeedItem:
    """
    Represent an element of the user feed.
    """
    client: object = None
    raw: object = None
    type: object = None

    def __repr__(self):
        return f'FeedItem(type={self.item_type})'

    def dictify(self, keys='all', recursive=False):
        """
        Convert the object to a dictionary.

        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.

        Returns:
            dict: A dict version of the object.
        """
        obj = utils.dictify(
            self, keys, ['user', 'header', 'item_type'], recursive)
        if 'html' in keys:
            obj['html'] = self.html.decode()
        return obj

    @cached_property
    def _soup(self):
        """
        Item soup.
        """
        try:
            from bs4 import BeautifulSoup as Soup
        except ImportError:
            print("\x1b[91mFeed parsing requires bs4 because i'm lazy.\x1b[0m")
            exit()
        return Soup(self.raw, 'html.parser')

    @cached_property
    def html(self):
        """
        Item HTML content.
        """
        return self._soup.find('div', {'class': 'feedRight'})

    @cached_property
    def header(self):
        """
        Item header (language dependent).
        """
        raw = self._soup.find('div', {'class': 'feedInfo'}).text
        return ' '.join(raw.split())

    @cached_property
    def user(self):
        """
        Item target.
        """
        from . import User
        user_url = self._soup.find('a', {'class': 'userLink'}).get('href')
        return User.get(self.client, utils.concat(consts.HOST, user_url))

    @cached_property
    def item_type(self):
        """
        Item type.
        """
        raw = consts.re.get_feed_type(self.raw)
        return consts.FEED_CLASS_TO_CONST.get(raw)


class _BaseQuality:
    """
    Represents a constant quality object that can selects
    itself among a list of qualities.
    """

    def __init__(self, value):
        """
        Initialize a new quality object.

        Args:
            value (Literal['best', 'half', 'worst'] | int | Self): String, number or quality object to initialize from.
        """
        self.value = value
        if isinstance(value, _BaseQuality):
            self.value = value.value
        elif isinstance(value, str):
            if consts.re.is_quality(value):
                self.value = int(value.replace('p', ''))
            else:
                assert value.lower() in ('best', 'half', 'worst')
        elif not isinstance(value, int):
            raise TypeError(f'Invalid quality: `{value}`')

    def __repr__(self):
        return f'phub.Quality({self.value})'

    def select(self, qualities):
        """
        Select among a list of qualities.

        Args:
            quals (dict): A dict containing qualities and URLs.

        Returns:
            str: The chosen quality URL.
        """
        keys = list(qualities.keys())
        if isinstance(self.value, str):
            if self.value == 'best':
                return qualities[max(keys)]
            elif self.value == 'worst':
                return qualities[min(keys)]
            else:
                return qualities[sorted(keys)[len(keys) // 2]]
        elif isinstance(self.value, int):
            if str(self.value) in keys:
                return qualities[str(self.value)]
            else:
                return qualities[utils.closest(keys, self.value)]
        raise TypeError('Internal error: quality type is', type(self.value))
