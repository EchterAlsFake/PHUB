from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import core

class Feed:
    
    def __init__(self, client: core.Client) -> None:
        '''
        Initialise a new feed object.
        '''
        
        self.client = client
    
    # TODO

# EOF