from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Self

from .. import utils

if TYPE_CHECKING:
    from . import User


@dataclass
class Tag:
    '''
    PHUB3 Tag representation
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
    
    raw: str = field(default = None, repr = False)
    user: User = field(default = None, repr = False)
    type: str = field(default = None, repr = False)
    
    @cached_property
    def text(self) -> NotImplemented:
        '''
        Text representation of the item.
        '''
        
        return NotImplemented

class _BaseQuality:
    '''
    Represents a constant quality object that can selects
    itself among a list of qualities.
    '''
    
    def __init__(self, value: Literal['best', 'half', 'worst'] | int | Self) -> None:
        '''
        Initialise a new quality object.
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