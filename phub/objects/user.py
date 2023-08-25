from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import core
    from .video import Video

from .. import utils
from .. import consts
from .. import errors

from .. import objects

class User:
    
    def __init__(self, client: core.Client, name: str = None, url: str = None) -> None:
        '''
        Initialise a new user object.
        '''
        
        self.client = client
        self.name = name
        self.url = url
    
    def __repr__(self) -> str:
        
        return f'phub.User(name={self.name})'

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
    def get(cls, user: str) -> Self:
        '''
        Fetch a user knowing its name or URL.
        '''
        
        # TODO
    
    @cached_property
    def videos(self) -> objects.HQuery:
        '''
        Get the list of videos published by this user.
        '''
        
        url = self.url.replace(consts.HOST, '')
        if '/model' in url: url += '/videos'
        
        return objects.HQuery(client = self.client, args = url)

# EOF