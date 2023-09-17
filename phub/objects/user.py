from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from ..core import Client
    from .video import Video

from .. import utils
from .. import consts
from .. import errors

from .. import objects

class User:

    def __init__(self, client: Client, name: str, url: str) -> None:
        '''
        Initialise a new user object.
        '''
        
        self.client = client
        self.name = name
        self.url = url
        
        # Save data keys so far so we can make a difference with the
        # cached property ones.
        self.loaded_keys = list(self.__dict__.keys()) + ['loaded_keys']
    
    def __repr__(self) -> str:
        
        return f'phub.User(name={self.name})'

    def refresh(self) -> None:
        '''
        Refresh user cache.
        '''
        
        # Clear properties cache
        for key in list(self.__dict__.keys()):
            if not key in self.loaded_keys:
                delattr(self, key)

    @classmethod
    def from_video(cls, video: Video) -> Self:
        '''
        Find the author of a video.
        '''
        
        if video.page is None:
            video.fetch('page@')
                
        guess = consts.re.video_model(video.page, throw = False) or \
                consts.re.video_channel(video.page, throw = False)
        
        if not guess:
            raise errors.RegexError('Could not find user for video', video)
        
        return cls(client = video.client, name = guess[1],
                   url = utils.concat(consts.HOST, guess[0]))
    
    @classmethod
    def get(cls, client: Client, user: str) -> Self:
        '''
        Fetch a user knowing its name or URL.
        
        NOTE - while using names only, multiple users can be found.
        '''
        
        if consts.re.is_url(user):
            name = url.split('/')[-1]
            url = user
        
        else:
            name = user.replace(' ', '-')
            
            # Guess the user type
            for type_ in ('model', 'pornstar', 'channels'):            
                
                guess = utils.concat(type_, name)
                response = client.call(guess, throw = False)
            
                if response.ok:
                    url = response.url
                    break
            
            else:
                raise errors.UserNotFound(f'User {user} not found.')
            
        return cls(client = client, name = name, url = url)
    
    @cached_property
    def videos(self) -> objects.HQuery:
        '''
        Get the list of videos published by this user.
        '''
        
        url = self.url.replace(consts.HOST, '')
        if 'model/' in url: url += '/videos'
                
        return objects.HQuery(client = self.client, args = url)

    @cached_property
    def page(self) -> str:
        '''
        The user page.
        '''
        
        return self.client.call(self.url).text

    @cached_property
    def bio(self) -> str | None:
        '''
        The user bio.
        '''
        
        return consts.re.user_bio(self.page, throw = False)

    @cached_property
    def info(self) -> dict[str, str]:
        '''
        The user detailled infos.
        
        [Experimental]
        
        Warning: language dependant.
        
        '''
        
        li = consts.re.user_infos(self.page)

        return {k: v for k, v in li} # TODO better parsing

# EOF