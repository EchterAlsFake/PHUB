from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, Literal, Union

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
                 servers: list[dict] = [],
                 name: str = 'image') -> None:
        '''
        Initialise a new image object.
        
        Args:
            client (Client): Parent client.
            url (str): The image URL.
            sizes (list[dict]): Image sizes/resolutions/servers.
            name (str): Image name.
        '''

        self.url = url
        self.name = name
        self.client = client
        self._servers = servers
        
        logger.debug('Generated new image object: %s', self)
        
        # Check server image sizes
        sizes = [s.get('size') for s in servers]
        
        if len(set(sizes)) > 1:
            logger.warning('Detected different image sizes on alt servers: %s', sizes)
    
    def __repr__(self) -> str:
        
        return f'phub.Image(name={self.name})'
    
    def download(self, path: os.PathLike = '.') -> str:
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
            
            try:
                raw = self.client.call(url).content
                file.write(raw)
                return path
                
            except Exception as err:
                
                logger.warning('Failed to get image `%s`', url)
                if not self._servers: raise err
                
                # Pop server and retry
                server = self._servers.pop(0)
                logger.info('Retrying download with server %s', server)
                self.url = server['src']
                self.download(path)

    def dictify(self,
                keys: Union[Literal['all'], list[str]] = 'all',
                recursive: bool = False) -> dict:
        '''
        Convert the object to a dictionary.
        
        Args:
            keys (str): The data keys to include.
            recursive (bool): Whether to allow other PHUB objects to dictify.
            
        Returns:
            dict: A dict version of the object.
        '''
        
        return utils.dictify(self, keys, ['url', 'name', '_servers'], recursive)
    
# EOF