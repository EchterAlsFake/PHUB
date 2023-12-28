from __future__ import annotations

import logging
from functools import cached_property
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self, Literal

from .. import utils
from .. import consts
from .. import errors

if TYPE_CHECKING:
    from ..core import Client
    from . import Video, Image
    from . import queries

logger = logging.getLogger(__name__)


@dataclass
class _QuerySupportIndex:
    '''
    Represents indexes about supported queries for a user and their built urls.
    '''
    
    videos: str = None
    upload: str = None

class User:
    '''
    Represents a Pornhub user.
    '''

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
                response = client.call(guess, 'HEAD', throw = False, silent = True)

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
    def _supports_queries(self) -> _QuerySupportIndex:
        '''
        Checks query support.
        '''
        
        index = _QuerySupportIndex()
        videos_url = utils.concat(self.url, 'videos')

        if utils.head(self.client, videos_url):
            index.videos = videos_url
        
        if self.type == 'pornstar' and \
           utils.head(self.client, upload_url := utils.concat(videos_url, 'upload')):
            index.upload = upload_url
        
        return index
    
    @cached_property
    def videos(self) -> queries.VideoQuery:
        '''
        Get the list of videos published by this user.
        '''
        
        from .query import queries
        
        # If the video page does not exists, we use the home page
        url = self._supports_queries.videos or self.url

        return queries.VideoQuery(client = self.client, func = url)
    
    @cached_property
    def uploads(self) -> queries.VideoQuery:
        '''
        Attempt to get the list of videos uploaded by this user.
        '''
        
        from .query import queries
        
        url = self._supports_queries.upload
        
        # If the user does not supports uploads, we just return an empty query.
        query = queries.VideoQuery
        if not url:
            logger.info('User %s does not support uploads', self)
            query = queries.EmptyQuery
        
        return query(self.client, func = url)
    
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

# EOF