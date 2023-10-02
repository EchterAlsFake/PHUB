from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Self, Callable

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

@dataclass
class Like:
    '''
    Represents video likes and their ratings.
    '''
    
    up: int
    down: int
    
    ratings: float = field(repr = False)

@dataclass
class FeedItem:
    '''
    Represent an element of the user feed.
    '''
    
    client: Client = field(default = None, repr = False)
    raw: str = field(default = None, repr = False)
    type: str = field(default = None, repr = False)
    
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

class Callback:
    
    def __init__(self, total: int) -> None:
        '''
        Initialise the callback with the segments count.
        '''
        
        self.total = total
    
    def on_start(self) -> None:
        '''
        Called on download process start.
        '''
    
    def on_download(self, progress: int) -> None:
        '''
        Called on download update.
        '''
        
    def on_write(self, progress: int) -> None:
        '''
        Called on file write update.
        '''
    
    def on_end() -> None:
        '''
        Called on download end.
        '''
        
    @classmethod
    def new(cls, obj: object | Callable, total: int) -> Self:
        '''
        Generate a new Callback given another
        Callback or a simple callback.
        '''
        
        if isinstance(obj, Callback):
            return Callback
        
        elif callable(obj):
            res = cls(total = total)
            
            def wrapper(_, progress):
                obj(progress, getattr(res, 'total'))
            
            cls.on_download = wrapper # Inject to on_download
            return res
        
        else:
            raise TypeError(f'Callback must be a function or a Callback instance')

# EOF