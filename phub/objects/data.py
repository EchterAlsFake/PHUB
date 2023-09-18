from dataclasses import dataclass, field

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

# EOF