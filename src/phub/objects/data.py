from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User

from .. import utils

@dataclass
class Tag:
    '''
    PHUB3 Tag representation
    '''
    
    name: str
    count: int = field(default = None, repr = False)

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