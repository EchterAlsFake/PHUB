from __future__ import annotations

from typing import TYPE_CHECKING
from functools import cache, cached_property

if TYPE_CHECKING:
    from ..core import Client

from .. import consts
from .. import errors

from . import Like
from .user import User
from .query import queries


class Playlist(queries.VideoQuery):
    '''
    Represents a Pornhub Playlist.
    Subclasses VideoQuery because it ressembles
    a lot to other Pornhub video pages (search, etc.)
    and it makes it possible to use .sample, .pages,
    etc. on it.
    '''
    
    def __init__(self, client: Client, pid: str) -> None:
        '''
        Initialise a new Playlist.
        
        Args:
            client (Client): Parent client to use.
            pid (str): The playlist id.
        '''
        
        # Initialise 
        super().__init__(client, func = None)
        
        # Define both playlist url (first page) and chunked (next pages)
        self.url = 'playlist/' + str(pid)
        self.chunk_url = f'playlist/viewChunked?id={pid}' '&token={token}&page={page}'
    
    @cached_property
    def _page(self) -> str:
        return self.client.call(self.url).text

    @cached_property
    def _token(self) -> str:
        return consts.re.get_token(self._page)
    
    @cache
    def _get_raw_page(self, index: int) -> str:
        '''
        Override for VideoQuery._get_raw_page.
        This method is originally supposed to fetch the
        raw content of a page and handle network errors,
        but we also use it to separate first page/chunked pages.
        '''
        
        if index == 0:
            self.hint = consts.re.container
            return self._page
        
        self.hint = consts.re.document
        
        response = self.client.call(self.chunk_url.format(page = index + 1,
                                                          token = self._token),
                                    throw = False)
        
        if response.status_code == 404:
            raise errors.NoResult()
        
        return response.text
    
    @cached_property
    def _data(self) -> str:
        return consts.re.playlist_data(self._page)

    def __len__(self) -> int:
        return int(consts.re.get_playlist_size(self._page))
    
    @cached_property
    def hidden_videos_amount(self) -> int:
        try:
            return int(consts.re.get_playlist_unavailable(self._page))

        # If no banner is there, then all videos are available
        except errors.RegexError: return 0

    @cached_property
    def like(self) -> Like:
        return Like(
            int(consts.re.get_playlist_likes(self._data)),
            int(consts.re.get_playlist_dislikes(self._data)),
            float(consts.re.get_playlist_ratings(self._data))
        )

    @cached_property
    def views(self) -> int:
        raw: str = consts.re.get_playlist_views(self._data)
        return int(raw.replace(',', ''))
    
    @cached_property
    def tags(self) -> list[str]:
        return consts.re.get_playlist_tags(self._data)

    @cached_property
    def author(self) -> User:
        url = consts.re.get_playlist_author(self._data)
        return User.get(self.client, consts.HOST + url)
    
    @cached_property
    def title(self) -> str:
        return consts.re.get_playlist_title(self._data)

# EOF