from __future__ import annotations

import logging
import re
from functools import cached_property
from typing import TYPE_CHECKING, Iterator

from urllib.parse import urlencode

import requests.exceptions

from . import Video
from .. import errors
from .. import consts

if TYPE_CHECKING:
    from ..core import Client

logger = logging.getLogger(__name__)


class Playlist:
    '''
    Represents a Pornhub playlist.
    '''

    # === Base methods === #
    def __init__(self, client: Client, url: str) -> None:
        '''
        Initialise a new playlist object.

        Args:
            client (Client): The parent client.
            url       (str): The playlist URL.
        '''

        if not consts.re.is_playlist(url):
            raise errors.URLError('Invalid video URL:', url)
        
        self.client = client
        self.url = url
        self.html_content = client.call(self.url).text

    @cached_property
    def videos(self) -> Iterator[Video]:
        page = 1
        has_more_videos = True
        playlist_id = re.search(r'/playlist/(.*?)', self.url).group(1)
        token = consts.re.get_token(self.html_content)

        while has_more_videos:
            # Construct the URL for fetching the playlist page
            try:
                params = {
                    'id': playlist_id,  # Assume this is set up elsewhere in your class
                    'token': token,  # Token provided at runtime
                    'page': page
                }
                # Use urlencode to properly format the query parameters for the URL
                query_string = urlencode(params)
                playlist_url = f"{self.url}?{query_string}"

                response = self.client.call(func=playlist_url)

                content = response.content.decode("utf-8")
                video_urls = [consts.HOST + "view_video" + video for video in consts.re.get_playlist_videos(content) if
                              "pkey=" in video]
                if video_urls:
                    # Remove duplicates
                    video_urls = list(set(video_urls))

                    for url in video_urls:
                        video = Video(self.client, url)
                        yield video
                    page += 1  # Prepare to load the next page
                else:
                    # No more videos found, stop the loop
                    has_more_videos = False

            except requests.exceptions.HTTPError:
                has_more_videos = False
                break
