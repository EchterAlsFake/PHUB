from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING
from functools import cached_property

from .. import utils

if TYPE_CHECKING:
    from ..core import Client


logger = logging.getLogger(__name__)


class Image:
    '''
    Represents an image hosted on Pornhub.
    (user avatar, video thumbnail, etc.)
    '''
    
    def __init__(self,
                 client: Client,
                 url: str,
                 sizes: list[dict] = None,
                 name: str = 'image') -> None:
        '''
        Initialise a new image object.
        
        Args:
            client    (Client): Parent client.
            url          (str): The image URL.
            sizes (list[dict]): Image sizes/resolutions/servers.
            name         (str): Image name.
        '''

        self.url = url
        self.name = name
        self._sizes = sizes
        self.client = client
        
        logger.debug('Generated new image object: %s', self)
    
    def __repr__(self) -> str:
        
        return f'phub.Image(name={self.name})'
    
    def download(self, path: str = '.') -> str:
        '''
        Download the image in a certain quality.
        
        Args:
            path (str): The download path.
        
        Returns:
            str: The image path if modified.
        
        TODO - Handle multiple qualities/sizes
        '''
        
        url = self.url
        _, ext = os.path.splitext(url)
        
        if os.path.isdir(path):
            path = utils.concat(path, self.name + ext)
        
        logger.info('Saving %s at %s', self, path)
        
        with open(path, 'wb') as file:
            
            raw = self.client.call(url).content
            file.write(raw)
        
        return path

# EOF