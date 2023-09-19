from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import User

from .. import utils

@dataclass
class Tag:
    name: str
    count: int = field(default = None, repr = False)

@dataclass
class Like:
    up: int
    down: int
    
    ratings: float = field(repr = False)

@dataclass
class FeedItem:
    raw: str = field(default = None, repr = False)
    user: object = field(default = None, repr = False) # User
    type: str = field(default = None, repr = False)

# EOF