
from __future__ import annotations

import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import core

from .. import utils

class Image:
    
    def __init__(self,
                 client: core.Client,
                 url: str,
                 sizes: list[dict] = None,
                 name: str = 'image') -> None:
        '''
        Initialise a new image object.
        '''

        self.url = url
        self.name = name
        self.client = client
    
    def __repr__(self) -> str:
        return f'phub.Image(name={self.name})'
    
    def download(self, path: str = '.') -> str:
        '''
        Download the image.
        '''
        
        _, ext = os.path.splitext(self.url)
        
        if os.path.isdir(path):
            path = utils.concat(path, self.name + ext)
        
        with open(path, 'wb') as file:
            
            raw = self.client.call(self.url).content
            file.write(raw)
        
        return path