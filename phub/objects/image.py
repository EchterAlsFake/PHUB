from __future__ import annotations

import os

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Client

from .. import utils

class Image:
    
    def __init__(self,
                 client: Client,
                 url: str,
                 sizes: list[dict] = None,
                 name: str = 'image') -> None:
        '''
        Initialise a new image object.
        '''

        self.url = url
        self.name = name
        self._sizes = sizes
        self.client = client
    
    def __repr__(self) -> str:
        return f'phub.Image(name={self.name} in {len(self.sizes)} sizes)'
    
    @cached_property
    def sizes(self) -> list[str]:
        '''
        The image sizes.
        '''
        
        # NOTE - I don't know if it is only with the tested videos,
        # but most of them only have one size with multiple urls.
        # return list(self._sizes.keys())
        
        # NOTE - With `avatar` images only, well, there is only one size.
        
        return []
    
    def download(self, path: str = '.', size: str = None) -> str:
        '''
        Download the image.
        '''
        
        if size:
            if not size in self._sizes:
                raise KeyError(f'{size} not disponible.')
            
            url = self._sizes[size]
        
        else:
            url = self.url
        
        _, ext = os.path.splitext(url)
        
        if os.path.isdir(path):
            path = utils.concat(path, self.name + ext)
        
        with open(path, 'wb') as file:
            
            raw = self.client.call(url).content
            file.write(raw)
        
        return path

# EOF