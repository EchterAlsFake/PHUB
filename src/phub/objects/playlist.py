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
        self.total_urls = self.video_urls()

    def video_urls(self):
        page = 1
        has_more_videos = True
        playlist_id = re.search(r'playlist/(\d+)', self.url).group(1)
        token = consts.re.get_token(self.html_content)
        total_urls = []
        while has_more_videos:
            # Construct the URL for fetching the playlist page
            try:
                params = {
                    'id': playlist_id,
                    'token': token,
                    'page': page
                }

                logger.info(f"Loading video page: {page}")
                query_string = urlencode(params)
                playlist_url = f"https://www.pornhub.com/playlist/viewChunked?{query_string}"
                response = self.client.call(func=playlist_url)
                content = response.content.decode("utf-8")
                video_urls = [consts.HOST + "view_video" + video for video in consts.re.get_playlist_videos(content) if
                              "pkey=" in video]
                if video_urls:
                    for url in video_urls:
                        total_urls.append(url)  # Not yielding the videos immediately, because PH will detect the high
                        # amount of traffic and stop providing us with the next videos of the pages

                    page += 1  # Prepare to load the next page
                else:
                    # No more videos found, stop the loop
                    logger.info("No more videos found")
                    has_more_videos = False

            except requests.exceptions.HTTPError as e:
                has_more_videos = False
                break

        return total_urls

    @cached_property
    def videos(self) -> Iterator[Video]:
        if len(self.total_urls) == 0 or self.total_urls is None:
            self.video_urls()

        for url in self.total_urls:
            yield Video(url=url, client=self.client)
