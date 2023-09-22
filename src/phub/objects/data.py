from __future__ import annotations

from typing import TYPE_CHECKING
from functools import cached_property
from dataclasses import dataclass, field

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

# EOF