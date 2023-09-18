from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Client

class Feed:
    
    def __init__(self, client: Client) -> None:
        '''
        Initialise a new feed object.
        '''
        
        self.client = client
    
    # TODO

# EOF