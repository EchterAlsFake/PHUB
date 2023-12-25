from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Self, Literal

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client
    from . import Video, Image
    from . import queries

logger = logging.getLogger(__name__)


class User:
    '''
    Represents a Pornhub user.
    '''

    def __new__(cls, client: Client, name: str, url: str, type: str = None) -> Self | Pornstar:
        '''
        Check user type.
        '''
        
        user_type = type or consts.re.get_user_type(url)
        
        if user_type == 'pornstar':
            return Pornstar(client, name, url, user_type)
        
        # ...
        
        return object.__new__(cls)
    
    def __init__(self, client: Client, name: str, url: str, type: str = None) -> None:
        '''
        Initialise a new user object.
        
        Args:
            client (Client): The client parent.
            name      (str): The user name.
            url       (str): The user page URL.
        '''
        
        self.client = client
        self.name = name
        self.url = consts.re.remove_host(url)
        self.type = type or consts.re.get_user_type(url)
        
        # Save data keys so far, so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
        
        logger.debug('Initialised new user object %s', self)
        
        # This attribute will be deleted if a refresh is triggered
        self._cached_avatar_url: str = None
    
    def __repr__(self) -> str:
        
        return f'phub.User(name={self.name})'

    def refresh(self) -> None:
        '''
        Refresh this instance cache.
        '''
        
        logger.info('Refreshing %s object', self)
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                logger.debug('Deleting key %s', key)
                delattr(self, key)

    def dictify(self,
                keys: Literal['all'] | list[str] = 'all',
                recursive: bool = False) -> dict:
            '''
            Convert the object to a dictionnary.
            
            Args:
                keys (str): The data keys to include.
                recursive (bool): Whether to allow other PHUB objects dictify. 
                
            Returns:
                dict: Dict version of the object.
            '''
            
            return utils.dictify(self, keys, ['name', 'url', 'type',
                                              'bio', 'info', 'avatar'], recursive)

    @classmethod
    def from_video(cls, video: Video) -> Self:
        '''
        Find the author of a video.
        
        Args:
            video (Video): A video object.
        '''
        
        if video.page is None:
            video.fetch('page@')
        
        guess = consts.re.video_model(video.page, throw = False) or \
                consts.re.video_channel(video.page, throw = False)
        
        if not guess:
            logger.error('Author of %s not found', video)
            raise errors.RegexError('Could not find user for video', video)
        
        return cls(client = video.client, name = guess[1],
                   url = utils.concat(consts.HOST, guess[0]))
    
    @classmethod
    def get(cls, client: Client, user: str) -> Self:
        '''
        Fetch a user knowing its name or URL.
        Note - Using only a username makes the fetch between
        1 and 3 times slower, you might prefer to use a direct
        URL.
        
        Args:
            client (Client): The parent client.
            user      (str): User name or URL.
        '''
        
        if consts.re.is_url(user):
            url = user
            user_type = (path := url.split('/'))[-2]
            name = path[-1]
        
        else:
            name = '-'.join(user.split())
            
            # Guess the user type
            for type_ in ('model', 'pornstar', 'channels'):            
                
                guess = utils.concat(type_, name)
                response = client.call(guess, 'HEAD', throw = False)

                # We need to verify that the guess is correct.
                # Pornhub redirects are weird, they depend on the
                # type of the user, so we need to make sure that
                # we are not redirected to avoid discret 404 pages
                if response.ok and type_ in response.url:
                    logger.info('Guessing type of %s is %s', user, type_)
                    url = response.url
                    user_type = type_
                    break
            
            else:
                logger.error('Could not guess type of %s', user)
                raise errors.UserNotFound(f'User {user} not found.')
        
        return cls(client = client, name = name, type = user_type, url = url)
    
    @cached_property
    def videos(self) -> queries.VideoQuery:
        '''
        Get the list of videos published by this user.
        '''
        
        from .query import queries
        
        return queries.VideoQuery(client = self.client,
                                  func = utils.concat(self.url, 'videos'))

    @cached_property
    def _page(self) -> str:
        '''
        The user page.
        '''
        
        return self.client.call(self.url).text

    @cached_property
    def bio(self) -> str | None:
        '''
        The user bio.
        '''
        
        return consts.re.user_bio(self._page, throw = False)

    @cached_property
    def info(self) -> dict[str, str]:
        '''
        The user detailed infos.
        
        [Experimental]
        
        Warning: keys depends on the lanugage.
        '''
        
        li = consts.re.user_infos(self._page)

        return {k: v for k, v in li} # TODO

    @cached_property
    def avatar(self) -> Image:
        '''
        The user avatar.
        '''
        
        from . import Image
        
        url = (getattr(self, '_cached_avatar_url')
               or consts.re.user_avatar(self._page))
        
        return Image(client = self.client,
                     url = url,
                     name = f'{self.name}-avatar')

class Pornstar(User):
    '''
    Represents a Pornstar.
    '''
    
    def __new__(cls, *args, **kwargs) -> Self:
        return object.__new__(cls)
    
    def __repr__(self) -> str:
        
        return f'phub.Pornstar(name={self.name})'
    
    @cached_property
    def uploads(self) -> queries.VideoQuery:
        '''
        The pornstar's custom uploads.
        '''
        
        from .query import queries
        
        return queries.VideoQuery(self.client, utils.concat(self.url, 'videos/upload'))
    
    @cached_property
    def videos(self) -> queries.VideoQuery:
        '''
        The pornstar's videos.
        '''
        
        from .query import queries
        
        return queries.VideoQuery(self.client, utils.concat(self.url, 'videos'))

# EOF