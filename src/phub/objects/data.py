from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Self

from .. import utils
from .. import consts

if TYPE_CHECKING:
    from .. import Client
    from . import User
    from bs4 import BeautifulSoup as Soup


@dataclass
class Tag:
    '''
    Video Tag representation.
    '''
    
    name: str
    count: int = field(default = None, repr = False)
    
    def __eq__(self, __value: object) -> bool:
        
        assert isinstance(__value, Tag)
        return self.name == __value.name
    
    def dictify(self,
                keys: Literal['all'] | list[str] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionnary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects dictify. 
        
        Returns:
            dict: Dict version of the object.
        '''
        
        return utils.dictify(self, keys, ['name', 'count'], recursive)

@dataclass
class Like:
    '''
    Represents video likes and their ratings.
    '''
    
    up: int
    down: int
    ratings: float = field(repr = False)
    
    def dictify(self,
                keys: Literal['all'] | list[str] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionnary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects dictify. 
        
        Returns:
            dict: Dict version of the object.
        '''
        
        return utils.dictify(self, keys, ['up', 'down', 'ratings'], recursive)

@dataclass
class FeedItem:
    '''
    Represent an element of the user feed.
    '''
    
    client: Client = field(default = None, repr = False)
    raw: str = field(default = None, repr = False)
    type: str = field(default = None, repr = False)
    
    def dictify(self,
                keys: Literal['all'] | list[str] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionnary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects dictify. 
        
        Returns:
            dict: Dict version of the object.
        '''
        
        obj = utils.dictify(self, keys, ['user', 'header', 'item_type'], recursive)
        if 'html' in keys: obj['html'] = self.html.decode()
        
        return obj
    
    @cached_property
    def _soup(self) -> Soup:
        '''
        Item soup.
        '''
        
        try:
            from bs4 import BeautifulSoup as Soup
        
        except ImportError:
            print('\033[91mFeed parsing requires bs4 because i\'m lazy.\033[0m')
            exit()
        
        return Soup(self.raw, 'html.parser')

    @cached_property
    def html(self) -> Soup:
        '''
        Item HTML content.
        '''
        
        return self._soup.find('div', {'class': 'feedRight'})
    
    @cached_property
    def header(self) -> str:
        '''
        Item header (language dependent).
        '''
        
        raw = self._soup.find('div', {'class': 'feedInfo'}).text
        return ' '.join(raw.split()) # Strip
    
    @cached_property
    def user(self) -> User:
        '''
        Item target.
        '''
        
        from . import User
        
        user_url = self._soup.find('a', {'class': 'userLink'}).get('href')
        return User.get(self.client, utils.concat(consts.HOST, user_url))
    
    @cached_property
    def item_type(self) -> str:
        '''
        Item type.
        '''
        
        from .. import locals
        
        raw = consts.re.get_feed_type(self.raw)
        
        return locals.FEED_CLASS_TO_CONST.get(raw)

class _BaseQuality:
    '''
    Represents a constant quality object that can selects
    itself among a list of qualities.
    '''
    
    def __init__(self, value: Literal['best', 'half', 'worst'] | int | Self) -> None:
        '''
        Initialise a new quality object.
        
        Args:
            value (Literal['best', 'half', 'worst'] | int | Self): String, number or quality object to initialise from.
        '''
        
        self.value = value
        
        if isinstance(value, _BaseQuality):
            self.value = value.value
        
        if isinstance(self.value, str):
            assert self.value.lower() in ('best', 'half', 'worst')
    
    def select(self, qualities: dict) -> str:
        '''
        Select among a list of qualities.
        
        Args:
            quals (dict): A dict containing qualities and URLs.
        
        Returns:
            str: The chosen quality URL.
        '''
        
        keys = list(qualities.keys())
        
        if isinstance(self.value, str):
            # Get approximative quality
            
            if self.value == 'best': return qualities[max(keys)]
            elif self.value == 'worst': return qualities[min(keys)]
            else: return qualities[ sorted(keys)[ len(keys) // 2 ] ]
        
        elif isinstance(self.value, int):
            # Get exact quality or nearest
            
            if (s:= str(self.value)) in keys: return qualities[s]
            else: return qualities[utils.closest(keys, self.value)]
        
        # This should not happen
        raise TypeError('Internal error: quality type is', type(self.value))

# EOF