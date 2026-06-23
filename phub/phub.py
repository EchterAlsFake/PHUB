"""
Copyright (C) 2026 Johannes Habel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import argparse
import os
import logging
import asyncio
import demjson3

from curl_cffi import Response, AsyncSession
from functools import cached_property
from typing import AsyncGenerator, Any, Literal, cast
from base_api.modules.type_hints import DownloadReport
from base_api.base import BaseCore, setup_logger, Helper
from base_api.modules.errors import InvalidProxy, UnknownError, NetworkingError, BotProtectionDetected

try:
    import lxml
    parser = "lxml" # Faster speeds, but more dependencies

except (ModuleNotFoundError, ImportError):
    parser = "html.parser" # Fallback to classic HTML parser (will work fine)

try:
    from modules.consts import *
    from modules.errors import *
    from modules.sorting import *
    from modules.type_hints import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *
    from .modules.errors import *
    from .modules.sorting import *
    from .modules.type_hints import *


async def on_error(url: str, error: Exception, attempt: int) -> bool:
    print(f"URL: {url}, ERROR: {error}, Attempt: {attempt}")

    if isinstance(error, ResourceGone):
        return False

    return True



async def get_html_content(core: BaseCore, url: str) -> str | None | dict:
    # What should I do here?
    try:
        content = await core.fetch(url)
        if isinstance(content, str):
            return content

        if isinstance(content, Response):
            if content.status_code == 404:
                raise NotFound(f"Server returned 404 for: {url}")

    except NetworkingError as e:
        raise NetworkError(str(e)) from e

    except InvalidProxy as e:
        raise ProxyError(str(e)) from e

    except BotProtectionDetected as e:
        raise BotDetection(str(e)) from e

    except UnknownError as e:
        raise UnknownNetworkError(str(e)) from e


class BaseObject:
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        self.url = url
        self.core = core
        self.html_content = html_content
        self._soup = None
        self.logger = setup_logger(name=f"PornHub API - [{self.__class__.__name__}]", log_file=None, level=logging.ERROR)

    async def _ensure_html(self):
        """Ensures that html_content is available by fetching it if necessary."""
        if not self.html_content:
            self.html_content = await get_html_content(core=self.core, url=self.url)

        assert isinstance(self.html_content, str)
        return self.html_content

    @property
    def soup(self) -> BeautifulSoup:
        """BeautifulSoup object. Triggers error if HTML fetch is missing and not already provided."""
        if self._soup is None:
            if not self.html_content:
                raise AttributeError(f"HTML content not available for {self.__class__.__name__}. Call 'await init()' first.")
            self._soup = BeautifulSoup(self.html_content, parser)
        return self._soup

    async def init(self):
        """Initializes the object by fetching HTML content."""
        await self._ensure_html()
        return self


class UserHelper(Helper, BaseObject):
    def __init__(self, url: str, core: BaseCore):
        BaseObject.__init__(self, url=url, core=core, html_content=None)
        self.core = core # Keep for Helper compatibility

    async def _make_video_safe(self, video_data: str | dict, **kwargs):
        """
        Ensures metadata dictionaries from extractors are handled correctly.
        """
        if isinstance(video_data, dict):
            url = video_data.pop("url")
            return Video(url, core=self.core, api_data=video_data)
        return Video(video_data, core=self.core)

    def enable_logging(self, log_file: str | None = None, level: int | None = None, log_ip: str | None = None, log_port: int | None = None):
        if not level:
            level = logging.DEBUG
        self.logger = setup_logger(name="PornHub API - [Pornstar]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    @cached_property
    def bio(self) -> str | None:
        try:
            return self.soup.find("div", class_="content js-headerContent js-highestChild").find("div", attrs={
                "itemprop": True}).text

        except AttributeError:
            return None

    @cached_property
    def about(self) -> str:
        return self.soup.find("section", class_="aboutMeSection sectionDimensions").find_all("div")[1].text.strip()

    @cached_property
    def info(self) -> dict:
        return_thing_idk_bro = {}

        container = self.soup.find("div", class_="content-columns inline js-highestChild js-headerContent")

        if not container:
            container = self.soup.find("div", class_="content-columns js-highestChild columns-2")

        stuff = container.find_all("div", class_="infoPiece")

        for thing in stuff:
            return_thing_idk_bro[thing.find_all("span")[0].text.strip()] = thing.find_all("span")[1].text.strip()

        return return_thing_idk_bro


    async def get_videos(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                         on_video_error: on_error_hint = on_error,
                         on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:
        page_urls = [f"{self.url}/videos?page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} pages...")
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                         max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield video


class SubscriptionHelper(Helper):
    def __init__(self, core: BaseCore):
        # We pass User as the dummy video class, but we'll use other_return
        super().__init__(core=core, video_constructor=User, alternative_constructor=self._make_user)

    async def _make_user(self, url: str):
        user = User(url=url, core=self.core)
        return await user.init()

    async def get_subscriptions(self, url: str, pages: int = 5, pages_concurrency: int | None = None,
                                videos_concurrency: int | None = None,
                                on_video_error: on_error_hint = on_error,
                                on_page_error: on_error_hint = None
                                ) -> AsyncGenerator[User, None]:
        page_urls = [f"{url}?page={page}" for page in range(1, pages + 1)]
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for user in self.iterator(target_page_urls=page_urls, video_link_extractor=extractor_users,
                                        use_alternative_constructor=True,
                                        max_page_concurrency=pages_concurrency,
                                        max_video_concurrency=videos_concurrency,
                                        on_video_error=on_video_error, on_page_error=on_page_error):
            yield user


class Pornstar(UserHelper):
    def __init__(self, url: str, core: BaseCore):
        # This calls UserHelper.__init__ correctly
        super().__init__(url=url, core=core)

    async def get_uploads(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                          on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None
                          ) -> \
            AsyncGenerator[Video, None]:
        page_urls = [f"{self.url}/videos/upload?page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} pages...")
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                         max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield video


    async def get_gifs(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                       on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None
                       ) -> \
    AsyncGenerator[GIF, None]:
        page_urls = [f"{self.url}/gifs/video?page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} pages...")
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for gif in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                       max_page_concurrency=pages_concurrency, video_link_extractor=extractor_gifs,
                                       on_video_error=on_video_error, on_page_error=on_page_error):
            yield await gif.init()


class Model(UserHelper):
    def __init__(self, url: str, core: BaseCore):
        super().__init__(url=url, core=core)


class User(UserHelper):
    def __init__(self, url: str, core: BaseCore):
        super().__init__(url=url, core=core)

    @cached_property
    def about(self) -> str:
        return self.soup.find("p", class_="aboutMeText").text.strip()

class Album(BaseObject):
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        super().__init__(url=url, core=core, html_content=html_content)
        self.script = None

    @cached_property
    def rating_percentage(self) -> str:
        return self.soup.find("div", attrs={"id": "ratingAlbumInfo"}).find("span").text.strip()

    @cached_property
    def votes(self) -> str:
        return self.soup.find("div", attrs={"id": "ratingAlbumInfo"}).find("div").text.strip()

    @cached_property
    def views(self) -> str:
        return self.soup.find("div", attrs={"id": "viewsPhotAlbumCounter"}).text.strip()

    @cached_property
    def publish_date(self) -> str:
        return self.soup.find("div", attrs={"id": "timeBlockContent"}).find_all("div")[1].text.strip().replace("Added", "").strip() # Don't ask

    @cached_property
    def tags(self) -> dict:
        return_random_thing_idk = {}

        stuff = self.soup.find("div", class_="photoBoxContContainer").find_all("div", class_="tagContainer")
        for a in stuff:
            text = a.text.strip()
            link = a.get("href")
            return_random_thing_idk.update({
                text: f"https://www.pornhub.com{link}"
            })

        return return_random_thing_idk

    @property
    async def author(self) -> Pornstar:
        if not hasattr(self, "_cached_author"):
            link = self.soup.find("span", class_="usernameBadgesWrapper").find("a").get("href")
            self._cached_author = await Pornstar(url=f"https://www.pornhub.com{link}", core=self.core).init()
        return self._cached_author

    async def get_photos(self, pages: int ) -> AsyncGenerator[dict, None]:
        page_urls = [f"{self.url}?page={page}" for page in range(1, pages + 1)]
        for idx, url in enumerate(page_urls):
            if idx == 0 and self.html_content:
                html_code = self.html_content

            else:
                html_code = await get_html_content(core=self.core, url=url)

            assert isinstance(html_code, str)
            soup = BeautifulSoup(html_code, parser)
            main_ul = soup.find("ul", class_="photosAlbumsListing albumViews preloadImage")
            li_tags = main_ul.find_all("div", class_="js_lazy_bkg photoAlbumListBlock")
            for li_tag in li_tags:
                link = f"https://www.pornhub.com{li_tag.find("a").get('href')}"
                spans = li_tag.find_all("span")
                rating = spans[0].text
                views = spans[1].text
                download_url = li_tag.get("data-bkg")

                thing = {
                    "url": link,
                    "download_url": download_url,
                    "rating": rating,
                    "views": views,
                }

                yield thing

    async def download_photo(self, url: str, path: str) -> bool:
        return await self.core.legacy_download(path=path, url=url)


class Short(BaseObject):
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        super().__init__(url=url, core=core, html_content=html_content)
        self._script: list | None = None
        self._metadata: dict | None= None

    async def init(self):
        # Shorts currently need HTML to find the JSON_SHORTIES script
        await self._ensure_html()

        scripts = self.soup.find_all("script")
        for script in scripts:
            if "JSON_SHORTIES" in script.text:
                stuff = re.search(r'JSON_SHORTIES = insertAfterNthPosition\((.*?), prerollObject', script.text, re.DOTALL).group(1)
                self._script = demjson3.decode(stuff)
                self._metadata = self._script[0]
        
        return self

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            # If accessed without init, it will fail if HTML is missing, 
            # but we assume init() is called for Shorts.
            return {}
        return self._metadata

    @cached_property
    def title(self) -> str:
        return cast(str, self.metadata.get("videoTitle"))

    @cached_property
    def video_id(self) -> int:
        return int(cast(int, self.metadata.get("videoId")))

    @cached_property
    def video_key(self) -> str:
        return cast(str, self.metadata.get("vkey"))

    @cached_property
    def favorites(self) -> int:
        return int(cast(int, self.metadata.get("favoriteInfo")))

    @cached_property
    def likes(self) -> int:
        return int(cast(int, self.metadata.get("likeNumber")))

    @cached_property
    def dislikes(self) -> int:
        return int(cast(int, self.metadata.get("dislikeNumber")))

    @cached_property
    def is_hd(self) -> bool:
        return True if self.metadata.get("isHD") == "True" else False

    @property
    async def get_video(self) -> Video:
        if not hasattr(self, "_cached_get_video"):
            self._cached_get_video = await Video(core=self.core, url=str(cast(str, self.metadata.get("linkUrl")))).init()
        return self._cached_get_video

    @cached_property
    def embed_url(self) -> str:
        return str(cast(str, self.metadata.get("embedUrl")))

    @cached_property
    def thumbnail(self) -> str:
        return str(cast(str, self.metadata.get("imageUrl")))

    @cached_property
    def mediaDefinitions(self):
        return self.metadata.get("mediaDefinitions")

    @cached_property
    def comment_count(self) -> int:
        return int(cast(int, self.metadata.get("commentCount")))

    @cached_property
    def avatar(self) -> str:
        return str(cast(str, self.metadata.get("avatar")))

    async def get_author(self) -> Pornstar:
        return await Pornstar(core=self.core, url=str(cast(str, self.metadata.get("profileUrl")))).init()

    @cached_property
    def author_name(self) -> str:
        return str(cast(str, self.metadata.get("name")))

    @cached_property
    def m3u8_base_url(self) -> str:
        """Builds a fake master.m3u8 playlist from quality-specific m3u8 URLs."""
        playlist_lines = ['#EXTM3U']
        for (width, height), uri in self.get_m3u8_urls.items():
            playlist_lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION={width}x{height}')
            playlist_lines.append(uri)
        return '\n'.join(playlist_lines)

    @cached_property
    def get_m3u8_urls(self) -> dict:
        '''
        The URL of the master M3U file.

        Args:
            quality (Quality): The video quality.

        Returns:
            str: The M3U url.
        '''

        quality_urls = {}
        raw_qualities = self.mediaDefinitions
        is_vertical = True

        def parse_quality(value: Any) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                digits = ''.join(ch for ch in value if ch.isdigit())
                if digits:
                    return int(digits)
            return 0

        def parse_quality_from_url(url: str) -> int:
            for part in url.split('/'):
                if 'P_' in part or 'p_' in part:
                    prefix = part.split('P_', 1)[0].split('p_', 1)[0]
                    return parse_quality(prefix)
            return 0

        def estimate_width(height: int) -> int:
            if height <= 0:
                return 0
            if is_vertical:
                return int(height * 9 / 16)
            return int(height * 16 / 9)

        for q in raw_qualities:
            if q.get('format') != 'hls' or not q.get('videoUrl'):
                continue

            try:
                width = int(q.get('width') or 0)
                height = int(q.get('height') or 0)
                url = q['videoUrl']

                if not height:
                    height = parse_quality(q.get('quality')) or parse_quality_from_url(url)
                if not width and height:
                    width = estimate_width(height)

                if not width and not height:
                    self.logger.warning(f"Skipping invalid quality entry: {q}, missing resolution data")
                    continue

                quality_urls[(width, height)] = url

            except Exception as e:
                self.logger.warning(f"Skipping invalid quality entry: {q}, {e}")
                continue
        return quality_urls

    async def download(self, quality, path="./", callback: callback_hint = None, no_title=False, remux: bool = False,
                 callback_remux: callback_hint=None, start_segment: int = 0, stop_event: asyncio.Event | None = None,
                 segment_state_path: str | None = None, segment_dir: str | None = None,
                 return_report: bool = False, cleanup_on_stop: bool = True, keep_segment_dir: bool = False
                 ) -> bool | DownloadReport:
        """
        :param callback:
        :param quality:
        :param path:
        :param no_title:
        :param remux:
        :param callback_remux:
        :param start_segment:
        :param stop_event:
        :param segment_state_path:
        :param segment_dir:
        :param return_report:
        :param cleanup_on_stop:
        :param keep_segment_dir:
        :return:
        """
        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")

        return await self.core.download(video=self, quality=quality, path=path, callback=callback, remux=remux,
                                         callback_remux=callback_remux, start_segment=start_segment,
                                         stop_event=stop_event,
                                         segment_state_path=segment_state_path, segment_dir=segment_dir,
                                         return_report=return_report,
                                         cleanup_on_stop=cleanup_on_stop, keep_segment_dir=keep_segment_dir)


class GIF(BaseObject):
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        super().__init__(url=url, core=core, html_content=html_content)
        self._script = None

    async def init(self):
        # We need HTML for GIF review status and LD+JSON
        await self._ensure_html()

        if "GIF is unavailable pending review." in self.html_content:
            raise GifPendingReview("The GIF is still pending a review and can't be downloaded yet...")

        if "This video has been disabled" in self.html_content:
            raise VideoDisabled("The Video has been disabled, I can not fetch any data from it.")
        
        return self

    def enable_logging(self, log_file: str | None = None, level: int | None = None, log_ip: str | None = None, log_port: int | None = None):
        if not level:
            level = logging.DEBUG
        self.logger = setup_logger(name="PornHub API - [GIF]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    @property
    def script(self):
        if self._script is None:
            self._script = json.loads(self.soup.find_all('script', type='application/ld+json')[0].text.replace('<script type="application/ld+json">', ""))
        return self._script

    @cached_property
    def title(self) -> str:
        if "name" in self.script:
            return self.script["name"]

        title_div = self.soup.find("div", class_="gifTitle")
        if title_div and title_div.find("h1"):
            return title_div.find("h1").text.strip()

        h1 = self.soup.find("h1")
        if h1:
            return h1.text.strip()

        return "Untitled GIF"

    @cached_property
    def vote_count(self) -> int:
        return int(self.soup.find("div", class_="voteCount").find("span").text.strip())

    @cached_property
    def vote_percentage(self) -> str:
        return self.soup.find("div", class_="votePercentage").find("span").text.strip()

    @cached_property
    def views(self) -> str:
        return self.soup.find("li", class_="float-right gifViews").text.strip()

    @cached_property
    def publish_date(self) -> str:
        return self.script["uploadDate"]

    @cached_property
    def thumbnail(self) -> str:
        return self.script["thumbnailUrl"]

    @cached_property
    def content_url(self) -> str:
        return self.script["contentUrl"]

    @cached_property
    def tags(self) -> dict:
        return_random_thing_idk = {}

        stuff = self.soup.find("ul", class_="tagList clearfix").find_all("li")
        for thing in stuff:
            link = thing.find("a")

            if link:
                first = thing.find("a").text.strip()
                href = thing.find("a").get("href")
                return_random_thing_idk[first] = href

        return return_random_thing_idk

    async def source_video(self):
        url = self.soup.find("div", class_="bottomMargin").find("a").get("href")
        return await Video(core=self.core, url=f"https://www.pornhub.com{url}").init()

    async def download(self, callback: callback_hint = None, path="./", no_title=False, stop_event: asyncio.Event | None = None) -> bool:
        """
        :param callback:
        :param path:
        :param no_title:
        :param stop_event:
        :return:
        """
        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")

        return await self.core.legacy_download(path=path, callback=callback, url=self.content_url, stop_event=stop_event)


class Channel(Helper, BaseObject):
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        BaseObject.__init__(self, url=url, core=core, html_content=html_content)
        self.core = core

    async def _make_video_safe(self, video_data: str | dict, **kwargs):
        if isinstance(video_data, dict):
            url = video_data.pop("url")
            return Video(url, core=self.core, api_data=video_data)
        return Video(video_data, core=self.core)

    @cached_property
    def name(self) -> str:
        return self.soup.find("div", class_="title floatLeft").find("h1").text.strip()

    @cached_property
    def is_award_winner(self) -> bool:
        if self.soup.find("i", class_="trophyChannel bg-trophy-channel tooltipTrig"):
            return True

        return False

    @cached_property
    def video_views(self) -> str:
        return self.soup.find_all("div", class_="info floatRight")[0].text.strip()

    @cached_property
    def subscribers(self) -> str:
        return self.soup.find_all("div", class_="info floatRight")[1].text.strip()

    @cached_property
    def total_videos(self) -> str:
        return self.soup.find_all("div", class_="info floatRight")[2].text.strip()

    @cached_property
    def rank(self) -> int:
        return int(self.soup.find_all("div", class_="info floatRight")[3].text.strip().replace("RANK", ""))

    @cached_property
    def description(self) -> str:
        return self.soup.find_all("p", class_="joined")[0].text.strip()

    @cached_property
    def join_date(self) -> str:
        return self.soup.find_all("p", class_="joined")[1].text.strip()

    @cached_property
    def website(self) -> str:
        return self.soup.find_all("p", class_="joined")[2].text.strip()

    async def get_user(self) -> User:
        link = self.soup.find_all("p", class_="joined")[3].find("a").get("href")
        link = f"https://www.pornhub.com{link}"
        user = User(core=self.core, url=link)
        return await user.init()

    async def get_videos(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                         on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None
                         ) -> AsyncGenerator[Video, None]:
        page_urls = [f"{self.url}videos?page={page}" for page in range(1, pages + 1)]
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                         max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield video


class Playlist(Helper, BaseObject):
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        BaseObject.__init__(self, url=url, core=core, html_content=html_content)
        self.core = core

    @cached_property
    def token(self) -> str:
        return REGEX_TOKEN.search(self.html_content).group(1)

    @cached_property
    def pid(self) -> str:
        return re.search(r'(\d+)/?$', self.url).group(1)

    @cached_property
    def title(self) -> str:
        return self.soup.find("h1", class_="playlistTitle watchPlaylistButton js-watchPlaylistHeader js-watchPlaylist").text.strip()

    @cached_property
    def views(self) -> str:
        return self.soup.find("div", class_="views").find("span").text.strip()

    @cached_property
    def rating_percent(self) -> str:
        return self.soup.find("div", class_="votes-count-container").find("span").text.strip()

    @cached_property
    def likes(self) -> int:
        return int(self.soup.find("div", class_="votes-count-container").find_all("span")[1].text.strip())

    @cached_property
    def dislikes(self) -> int:
        return int(self.soup.find("div", class_="votes-count-container").find_all("span")[2].text.strip())

    async def get_author(self) -> User:
        div = self.soup.find("div", class_="usernameWrap clearfix").find("a").get("href")
        url = f"https://www.pornhub.com{div}"
        user = User(core=self.core, url=url)
        return await user.init()

    @cached_property
    def video_count(self) -> int:
        stuff = self.soup.find("div", attrs={"id": "js-aboutPlaylistTabView"}).find("div").text.strip()
        return int(re.search(r'(\d+)\s*videos', stuff).group(1))

    @cached_property
    def tags(self) -> dict:
        random_return_thing_idk_bro = {}

        container = self.soup.find("div", class_="tagsWrap js-tagsWrap")
        tags = container.find_all("a")
        for tag in tags:
            name = tag.get("data-label")
            link = f"https://www.pornhub.com{tag.get('href')}"
            random_return_thing_idk_bro[str(name)] = link

        return random_return_thing_idk_bro

    @cached_property
    def description(self) -> str:
        return self.soup.find("p", class_="description js-playlistDescription").find("span").text.strip()

    @cached_property
    def unavailable_videos_count(self) -> int:
        assert isinstance(self.html_content, str)
        stuff = re.search(r'unavailable videos that are hidden:\s+(\d+)', self.html_content)
        return int(stuff.group(1))

    async def get_videos(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None,
                         on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency

        # Process the initial page (self.html_content) if pages >= 1
        if pages >= 1:
            # Use extractor_videos for the initial full HTML page content from
            # self.html_content
            # This is critical because the initial page's structure is different from chunked responses.
            assert isinstance(self.html_content, str)
            initial_page_links = extractor_videos_from_playlist_page(self.html_content)
            # Initialize videos concurrently in the background
            tasks = [asyncio.create_task(Video(url=link, core=self.core).init()) for link in initial_page_links]
            for task in tasks:
                yield await task

        # Generate URLs for subsequent chunked pages
        # Start from page 2 (index 1) since page 1 (index 0) was handled above
        chunked_page_urls = [
            f'https://www.pornhub.com/playlist/viewChunked?id={self.pid}&token={self.token}&page={page}'
            for page in range(2, pages + 1)
        ]

        if chunked_page_urls:
            # Use self.iterator with extractor_videos_playlist for chunked pages
            async for video in self.iterator(target_page_urls=chunked_page_urls, max_video_concurrency=videos_concurrency,
                                             max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos_playlist,
                                             on_video_error=on_video_error, on_page_error=on_page_error):
                yield await video


class Video(BaseObject):
    def __init__(self, url, core: BaseCore, html_content=None, api_data: dict | None = None, force_scraping: bool = False):
        super().__init__(url=url, core=core, html_content=html_content)
        self._api_data = api_data
        self.force_scraping = force_scraping

    async def init(self):
        if "/gif/" in self.url:
            return await GIF(url=self.url, core=self.core, html_content=self.html_content).init()

        if self.force_scraping:
            await self.ensure_html()
            return self

        if self._api_data or self.html_content:
            return self

        # Default to Webmaster API for initialization if no data provided
        try:
            data = await self.get_api_data()
            if "video" in data:
                self._api_data = data["video"]
            else:
                self._api_data = data
        except Exception as e:
            self.logger.warning(f"Failed to fetch HubTraffic API data for {self.url}: {e}")
            pass

        return self

    @property
    def api_data(self) -> dict:
        return self._api_data

    @api_data.setter
    def api_data(self, value: dict):
        self._api_data = value

    async def ensure_html(self):
        """Manually trigger HTML fetch if we need deep scraping."""
        return await self._ensure_html()

    async def get_api_data(self) -> dict:
        """
        This uses PornHubs Webmaster API which is way faster for scraping as it results in json, however
        this does not give us all video attributes and those who aren't supported need to be additionally
        fetched by using HTML scraping
        :return:
        """
        stuff = await self.core.fetch(f"https://www.pornhub.com/webmasters/video_by_id?id={self.video_id}", get_response=True)
        assert isinstance(stuff, Response)
        return stuff.json()


    def enable_logging(self, log_file: str | None = None, level: int | None = None, log_ip: str | None = None, log_port: int | None = None):
        if not level:
            level = logging.DEBUG
        self.logger = setup_logger(name="PornHub API - [Video]", log_file=log_file, level=level, http_ip=log_ip, http_port=log_port)

    @cached_property
    def video_id(self) -> str:
        return re.search(r"viewkey=([^&#]+)", self.url).group(1)

    @cached_property
    def soup(self) -> BeautifulSoup:
        if self._soup is None and self.html_content:
            self._soup = BeautifulSoup(self.html_content, parser)

        return self._soup

    @cached_property
    def flashvars(self) -> dict:
        if not self.html_content:
            raise ValueError("You need to call: await video.ensure_html() before downloading!")

        match = REGEX_VIDEO_FLASHVARS.search(self.html_content)
        stuff = match.group(1)
        return json.loads(stuff, strict=False)

    @cached_property
    def is_vr(self) -> bool:
        if self.api_data:
            return False # HubTraffic doesn't seem to specify VR
        return False if self.flashvars["isVR"] == 0 else True

    @cached_property
    def is_video_unavailable(self) -> bool:
        if self.api_data:
            return False
        return False if self.flashvars["video_unavailable"] == "false" else True

    @cached_property
    def is_hd(self) -> bool:
        if self.api_data:
            # HubTraffic doesn't explicitly say HD, but we can guess or it might be in some fields
            return False 
        return False if self.flashvars["isHD"] == "false" else True

    @cached_property
    def duration(self) -> int:
        if self.api_data:
            dur = self.api_data.get("duration")
            if isinstance(dur, str) and ":" in dur:
                parts = dur.split(":")
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return int(dur) if dur else 0
        return int(self.flashvars["video_duration"])

    @cached_property
    def title(self) -> str:
        if self.api_data:
            return str(cast(str, self.api_data.get("title")))
        return self.flashvars["video_title"]

    @cached_property
    def thumbnail(self) -> str:
        if self.api_data:
            return str(cast(str, self.api_data.get("default_thumb"))) or str(cast(str, self.api_data.get("thumb")))
        return self.flashvars["image_url"]

    @cached_property
    def available_qualities(self) -> list:
        quals = self.flashvars["defaultQuality"]
        return sorted(quals)

    @cached_property
    def is_vertical(self) -> bool:
        return True if self.flashvars["isVertical"] == "true" else False

    @cached_property
    def is_video_unavailable_in_your_country(self) -> bool:
        return True if self.flashvars["video_unavailable_country"] == "true" else False

    @cached_property
    def m3u8_base_url(self) -> str:
        """Builds a fake master.m3u8 playlist from quality-specific m3u8 URLs."""
        playlist_lines = ['#EXTM3U']
        for (width, height), uri in self.get_m3u8_urls.items():
            playlist_lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION={width}x{height}')
            playlist_lines.append(uri)
        return '\n'.join(playlist_lines)

    @cached_property
    def get_m3u8_urls(self) -> dict:
        '''
        The URL of the master M3U file.

        Args:
            quality (Quality): The video quality.

        Returns:
            str: The M3U url.
        '''

        quality_urls = {}
        raw_qualities = self.flashvars["mediaDefinitions"]
        is_vertical = self.is_vertical

        def parse_quality(value: Any) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                digits = ''.join(ch for ch in value if ch.isdigit())
                if digits:
                    return int(digits)
            return 0

        def parse_quality_from_url(url: str) -> int:
            for part in url.split('/'):
                if 'P_' in part or 'p_' in part:
                    prefix = part.split('P_', 1)[0].split('p_', 1)[0]
                    return parse_quality(prefix)
            return 0

        def estimate_width(height: int) -> int:
            if height <= 0:
                return 0
            if is_vertical:
                return int(height * 9 / 16)
            return int(height * 16 / 9)

        for q in raw_qualities:
            if q.get('format') != 'hls' or not q.get('videoUrl'):
                continue

            try:
                width = int(q.get('width') or 0)
                height = int(q.get('height') or 0)
                url = q['videoUrl']

                if not height:
                    height = parse_quality(q.get('quality')) or parse_quality_from_url(url)
                if not width and height:
                    width = estimate_width(height)

                if not width and not height:
                    self.logger.warning(f"Skipping invalid quality entry: {q}, missing resolution data")
                    continue

                quality_urls[(width, height)] = url

            except Exception as e:
                self.logger.warning(f"Skipping invalid quality entry: {q}, {e}")
                continue
        return quality_urls

    @cached_property
    def views(self) -> str:
        if self.api_data:
            return str(self.api_data.get("views", "0"))
        return self.soup.find("div", class_="video-actions-menu ctasActionMenu").find("div", class_="views").find("span").text

    @cached_property
    def publish_date(self) -> str:
        if self.api_data:
            return self.api_data.get("publish_date", "")
        return self.soup.find("div", class_="video-actions-menu ctasActionMenu").find("div", class_="videoInfo").text

    @cached_property
    def rating_percent(self) -> str:
        return str(cast(str, self.api_data.get("rating")))

    @cached_property
    def likes(self) -> str:
        if self.api_data:
            return str(self.api_data.get("ratings", "0"))
        return self.soup.find("span", class_="votesUp").text

    @cached_property
    def categories(self) -> dict | list:
        return_thing_idk_bro = []

        if self.api_data:
            tags = cast(list, self.api_data.get("categories"))
            if tags:
                for tag in tags:
                    return_thing_idk_bro.append(tag["category"])

            return return_thing_idk_bro

        return_thing_idk_bro = {}

        stuff = self.soup.find("div", class_ = "categoriesWrapper").find_all("a", class_="gtm-event-video-underplayer item")
        for thing in stuff:
            first = thing.text
            href = thing.get("href")
            return_thing_idk_bro[first] = href

        return return_thing_idk_bro

    @cached_property
    def author_thumbnail(self) -> str:
        return str(cast(str, self.soup.find("div", class_="userAvatar").find("img").get("src")))

    @cached_property
    def tags(self) -> dict | list:
        return_thing_idk_bro = []

        if self.api_data:
            tags = cast(list, self.api_data.get("tags"))
            if tags:
                for tag in tags:
                    return_thing_idk_bro.append(tag["tag_name"])

            return return_thing_idk_bro

        return_thing_idk_bro = {}

        stuff = self.soup.find("div", class_ = "tagsWrapper").find_all("a", class_="video_underplayer")
        for thing in stuff:
            first = thing.text
            href = thing.get("href")
            return_thing_idk_bro[first] = href

        return return_thing_idk_bro

    @property
    async def author(self) -> Pornstar | Channel | Model:
        if not hasattr(self, "_cached_author"):
            link = self.soup.find("div", class_="userAvatar").find("a").get("href")
            link = f"https://www.pornhub.com{link}"

            if "pornstar" in link:
                pornstar = Pornstar(core=self.core, url=link)
                self._cached_author = await pornstar.init()

            elif "model" in link:
                model = Model(core=self.core, url=link)
                self._cached_author = await model.init()

            elif "channel" in link:
                channel = Channel(core=self.core, url=link)
                self._cached_author = await channel.init()
            else:
                self._cached_author = None
        return self._cached_author

    def author_dict(self) -> dict:
        stuff = self.soup.find("div", class_="userInfo")
        a_tag = stuff.find("span", clas_="usernameBadgesWrapper").find("a")

        name = a_tag.text
        link = a_tag.get("href")
        link = f"https://www.pornhub.com/{link}"

        video_amount = stuff.find_all("span")[1].text
        subscriber_amount = stuff.find_all("span")[2].text

        return {
            "name": name,
            "link": {link},
            "video_amount": video_amount,
            "subscriber_amount": subscriber_amount
        }

    async def download(self, quality, path="./", callback: callback_hint=None, no_title=False, remux: bool = False,
                 callback_remux: callback_hint=None, start_segment: int = 0, stop_event: asyncio.Event | None = None,
                 segment_state_path: str | None = None, segment_dir: str | None = None,
                 return_report: bool = False, cleanup_on_stop: bool = True, keep_segment_dir: bool = False
                 ) -> bool | DownloadReport:
        """
        :param callback:
        :param quality:
        :param path:
        :param no_title:
        :param remux:
        :param callback_remux:
        :param start_segment:
        :param stop_event:
        :param segment_state_path:
        :param segment_dir:
        :param return_report:
        :param cleanup_on_stop:
        :param keep_segment_dir:
        :return:
        """
        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")

        return await self.core.download(video=self, quality=quality, path=path, callback=callback, remux=remux,
                                         callback_remux=callback_remux, start_segment=start_segment,
                                         stop_event=stop_event,
                                         segment_state_path=segment_state_path, segment_dir=segment_dir,
                                         return_report=return_report,
                                         cleanup_on_stop=cleanup_on_stop, keep_segment_dir=keep_segment_dir)



class Image:
    def __init__(self, core: BaseCore, url: str, name: str = 'image'):
        self.core = core
        self.url = url
        self.name = name

    def __repr__(self) -> str:
        return f"Image(name={self.name})"


class Account:
    def __init__(self, client: Client):
        self.client = client
        self.name: str | None = None
        self.avatar: Image | None = None
        self.is_premium: bool = False
        self.user: User | None = None

    def connect(self, data: dict):
        self.name = data.get('username')
        self.avatar = Image(self.client.core, str(cast(str, data.get('avatar'))), name='avatar')
        self.is_premium = data.get('premium_redirect_cookie') != '0'

        if self.name:
            url = f"https://www.pornhub.com/users/{self.name}"
            self.user = User(url=url, core=self.client.core)

    async def get_recommended(self, pages: int = 5, force_scraping: bool = False) -> AsyncGenerator[Video, None]:
        async for video in self.client.get_recommended(pages=pages, force_scraping=force_scraping):
            yield video

    async def get_history(self, pages: int = 5, force_scraping: bool = False) -> AsyncGenerator[Video, None]:
        async for video in self.client.get_history(pages=pages, force_scraping=force_scraping):
            yield video

    async def get_favorites(self, pages: int = 5, force_scraping: bool = False) -> AsyncGenerator[Video, None]:
        async for video in self.client.get_favorites(pages=pages, force_scraping=force_scraping):
            yield video

    async def get_feed(self, section: str = 'videos', pages: int = 5, force_scraping: bool = False) -> AsyncGenerator[Video, None]:
        async for video in self.client.get_feed(section=section, pages=pages, force_scraping=force_scraping):
            yield video

    async def get_subscriptions(self, pages: int = 5) -> AsyncGenerator[User, None]:
        async for user in self.client.get_subscriptions(pages=pages):
            yield user

    def __repr__(self) -> str:
        status = 'logged-out' if self.name is None else f'name={self.name}'
        return f'Account({status})'


class Client(Helper):
    def __init__(self, core: BaseCore = BaseCore(), email: str | None = None, password: str | None = None, login: bool = False):
        super().__init__(core, video_constructor=Video)
        self.core = core or BaseCore()
        self.core.initialize_session()
        assert isinstance(self.core.session, AsyncSession)
        self.core.session.headers.update(HEADERS)
        self.core.session.cookies.update(COOKIES)
        self.logger = setup_logger(name="PornHub API - [Client]", log_file=None, level=logging.ERROR)

        self.credentials = {"email": email, "password": password}
        self.logged = False
        self.account = Account(self)

        if login and email and password:
            asyncio.create_task(self.login())

    async def login(self, force: bool = False, throw: bool = True) -> bool:
        """
        Attempt to log in asynchronously.
        """
        self.logger.debug("Attempting login")

        if not force and self.logged:
            self.logger.error("Client is already logged in")
            if throw:
                raise ClientAlreadyLogged()
            return True

        if not self.credentials["email"] or not self.credentials["password"]:
            self.logger.error("Email and password are required for login")
            if throw:
                raise LoginFailed("Email and password are required")
            return False

        # Get token from homepage
        page_content = await get_html_content(url=HOST, core=self.core)
        match = REGEX_TOKEN.search(page_content)
        if not match:
            self.logger.error("Could not find login token")
            if throw:
                raise LoginFailed("Could not find login token")
            return False

        token = match.group(1)

        # Send credentials
        payload = LOGIN_PAYLOAD | self.credentials | {"token": token}
        
        url = f"{HOST}front/authenticate"
        try:
            response = await self.core.fetch(url, method="POST", data=payload, get_response=True)
            assert isinstance(response, Response)
            data = response.json()
        except Exception as e:
            self.logger.error(f"Login request failed: {e}")
            if throw:
                raise LoginFailed(f"Login request failed: {e}")
            return False

        success = int(data.get("success", 0))
        message = data.get("message", "Unknown error")

        if not success:
            self.logger.error(f"Login failed: {message}")
            if throw:
                raise LoginFailed(message)
            return False

        # Update account data
        self.account.connect(data)
        self.logged = True
        return True

    async def fix_recommendations(self) -> bool:
        """
        Allow recommendations cookies.
        """
        if not self.logged:
            return False

        self.logger.info("Fixing account recommendations")
        
        # Get token
        page_content = await get_html_content(url=HOST, core=self.core)
        match = REGEX_TOKEN.search(page_content)
        if not match:
            return False
        token = match.group(1)

        params = {
            'token': token,
            'cookie_selection': 3,
            'site_id': 1
        }
        url = f"{HOST}user/log_user_cookie_consent"
        try:
            response = await self.core.fetch(url, params=params, get_response=True)
            assert isinstance(response, Response)
            return response.json().get("success", False)
        except Exception:
            return False

    async def get_recommended(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None, force_scraping: bool = False,
                              on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:
        """
        Get recommended videos for the logged-in account.
        """
        if not self.logged:
            self.logger.warning("Client not logged in, recommended videos might not be personalized")

        await self.fix_recommendations()

        base_url = f"{HOST}recommended"
        page_urls = [f"{base_url}?page={page}" for page in range(1, pages + 1)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                       max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos, force_scraping=force_scraping,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield await video

    async def get_history(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None, force_scraping: bool = False,
                          on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None
                          ) -> AsyncGenerator[Video, None]:
        """
        Get watch history for the logged-in account.
        """
        if not self.logged:
            raise LoginFailed("Must be logged in to access history")

        base_url = f"{HOST}users/{self.account.name}/videos/recent"
        page_urls = [f"{base_url}?page={page}" for page in range(1, pages + 1)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                       max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos, force_scraping=force_scraping,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield await video

    async def get_favorites(self, pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None, force_scraping: bool = False,
                            on_video_error: on_error_hint = on_error,   on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:
        """
        Get favorite videos for the logged-in account.
        """
        if not self.logged:
            raise LoginFailed("Must be logged in to access favorites")

        base_url = f"{HOST}users/{self.account.name}/videos/favorites"
        page_urls = [f"{base_url}?page={page}" for page in range(1, pages + 1)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency

        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                       max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos, force_scraping=force_scraping,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield await video

    async def get_feed(self, section: str = 'videos', pages: int = 5, videos_concurrency: int | None = None, pages_concurrency: int | None = None, force_scraping: bool = False,
                       on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[Video, None]:
        """
        Get the account feed.
        :param force_scraping:
        :param pages_concurrency:
        :param videos_concurrency:
        :param section: Section to filter (videos, photos, posts, etc.)
        :param on_video_error:
        :param on_page_error:
        :param pages: Number of pages to fetch.
        """
        if not self.logged:
            raise LoginFailed("Must be logged in to access feed")

        base_url = f"{HOST}feeds?section={section}"
        page_urls = [f"{base_url}&page={page}" for page in range(1, pages + 1)]

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency

        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                         max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos, force_scraping=force_scraping,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield await video

    async def get_subscriptions(self, pages: int = 5, pages_concurrency: int | None = None, videos_concurrency: int | None = None,
                                on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[User, None]:
        """
        Get the account subscriptions.
        """
        if not self.logged:
            raise LoginFailed("Must be logged in to access subscriptions")

        url = f"{HOST}users/{self.account.name}/subscriptions"
        helper = SubscriptionHelper(core=self.core)
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for user in helper.get_subscriptions(url=url, pages=pages, pages_concurrency=pages_concurrency, videos_concurrency=videos_concurrency,
                                                   on_video_error=on_video_error, on_page_error=on_page_error):
            yield user

    async def iterator(self, *args, force_scraping: bool = False, **kwargs):
        self._force_scraping = force_scraping
        if "page_urls" in kwargs:
            kwargs["target_page_urls"] = kwargs.pop("page_urls")
        if "videos_concurrency" in kwargs:
            kwargs["max_video_concurrency"] = kwargs.pop("videos_concurrency")
        if "pages_concurrency" in kwargs:
            kwargs["max_page_concurrency"] = kwargs.pop("pages_concurrency")
        if "extractor" in kwargs:
            kwargs["video_link_extractor"] = kwargs.pop("extractor")
        try:
            async for item in super().iterator(*args, **kwargs):
                yield item
        finally:
            self._force_scraping = False

    async def _make_video_safe(self, video_data: str | dict, **kwargs):
        """
        Overrides Helper._make_video_safe to avoid HTML fetching by default.
        Supports both raw URLs and metadata dictionaries.
        """
        force = getattr(self, "_force_scraping", False)
        if isinstance(video_data, dict):
            url = video_data.pop("url")
            # If metadata says it's from search, we can treat it as api_data for the Video object
            # This avoids fetching the video page HTML during search/iteration
            return Video(url, core=self.core, api_data=video_data, force_scraping=force)
        
        # If it's just a URL string, we create a Video object without fetching HTML yet
        return Video(video_data, core=self.core, force_scraping=force)

    def enable_logging(self, log_file: str | None = None, level: int | None =None, log_ip: str | None = None, log_port: int | None = None):
        if not level:
            level = logging.DEBUG
        self.logger = setup_logger(name="PornHub API - [Client]", log_file=log_file, level=level, http_ip=log_ip,
                                   http_port=log_port)

    async def get_video(self, url: str, force_scraping: bool = False) -> Video:
        """
        :param url: (str) The video URL
        :param force_scraping: (bool) Whether to force web scraping instead of using the API
        :return: (Video) The video object
        """
        video = Video(url, core=self.core, force_scraping=force_scraping)
        return await video.init()

    async def get_pornstar(self, url: str) -> Pornstar:
        """
        :param url: (str) The Pornstar URL
        :return: (Video) The Pornstar object
        """
        pornstar = Pornstar(url, core=self.core)
        return await pornstar.init()

    async def get_gif(self, url: str) -> GIF:
        """
        param url: (str) The GIF URL
        :return: (GIF) The GIF object
        """
        gif = GIF(url, core=self.core)
        return await gif.init()

    async def get_album(self, url: str) -> Album:
        """
        param url: (str) The Album URL:
        :param url:
        :return:
        """
        album = Album(url, core=self.core)
        return await album.init()

    async def get_short(self, url: str) -> Short:
        """
        param url: (str) The Short URL:
        :param url:
        :return:
        """
        short = Short(url, core=self.core)
        return await short.init()

    async def get_model(self, url: str) -> Model:
        """
        param url: (str) The Model URL:
        :param url:
        :return:
        """
        model = Model(url, core=self.core)
        return await model.init()

    async def get_user(self, url: str) -> User:
        """
        param url: (str) The User URL:
        :param url:
        :return:
        """
        user = User(url, core=self.core)
        return await user.init()

    async def get_playlist(self, url: str) -> Playlist:
        playlist = Playlist(url=url, core=self.core)
        return await playlist.init()

    async def get_channel(self, url: str) -> Channel:
        channel = Channel(url=url, core=self.core)
        return await channel.init()

    async def search_gifs(self, query: str, category: Literal["gay", "transgender"] | None = None,
                          search_filter: Literal["mr", "mv", "tr"] | None = None,
                          pages: int = 5,
                          pages_concurrency: int | None = None, videos_concurrency: int | None = None,
                          on_video_error: on_error_hint = on_error, on_page_error: on_error_hint = None) -> AsyncGenerator[GIF, None]:
        """
        :param search_filter: [mr = Most Recent, mv = Most Viewed, tr = Top Rated] Default: Most relevant
        :param category: [gay, transgender] Default: Straight
        :param query:
        :param pages: Default: 5
        :param videos_concurrency:
        :param pages_concurrency:
        :return:
        """

        base_url = "https://www.pornhub.com/"

        if category:
            base_url += category + "/"

        base_url += f"gifs/search?search={query}"
        if search_filter:
            base_url += f"&o={search_filter}"

        page_urls = [f"{base_url}&page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} pages...")
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for gif in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                         max_page_concurrency=pages_concurrency, video_link_extractor=extractor_gifs,
                                       on_video_error=on_video_error, on_page_error=on_page_error):
            yield await gif.init()

    async def search_videos(self, query: str, production_type: Literal["professional", "homemade"] | None = None,
                            sort_by: Literal["mr", "mv", "tr"] | None = None,
                            duration_min: Literal["10", "20", "30"] | None = None,
                            duration_max: Literal["10", "20", "30"] | None = None,
                            pages: int = 5,
                            videos_concurrency: int | None = None,
                            pages_concurrency: int | None = None,
                            force_scraping: bool = False,
                            on_video_error: on_error_hint = on_error,
                            on_page_error: on_error_hint = None
                            ) -> AsyncGenerator[Video, None]:
        base_url = f"https://www.pornhub.com/video/search?search={query}"
        if production_type:
            base_url += f"&p={production_type}"

        if sort_by:
            base_url += f"&o={sort_by}"

        if duration_min:
            base_url += f"&duration_min={duration_min}"

        if duration_max:
            base_url += f"&duration_max={duration_max}"

        page_urls = [f"{base_url}&page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} pages...")
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency
        async for video in self.iterator(target_page_urls=page_urls, max_video_concurrency=videos_concurrency,
                                       max_page_concurrency=pages_concurrency, video_link_extractor=extractor_videos, force_scraping=force_scraping,
                                         on_video_error=on_video_error, on_page_error=on_page_error):
            yield video

    async def search_hubtraffic(self, query: str,
                                 category: str | None = None,
                                 sort_by: Literal["newest", "mostviewed", "rating"] | None = None,
                                 period: Literal["weekly", "monthly", "alltime"] | None = None,
                                 pages: int = 5,
                                 pages_concurrency: int = 5,
                                 ) -> AsyncGenerator[Video, None]:
        """
        Search for videos using the HubTraffic API (Webmaster API).
        This is faster and provides pre-parsed metadata.
        """
        base_url = f"https://www.pornhub.com/webmasters/search?search={query}"
        if category:
            base_url += f"&category={category}"
        if sort_by:
            base_url += f"&ordering={sort_by}"
        if period:
            base_url += f"&period={period}"

        page_urls = [f"{base_url}&page={page}" for page in range(1, pages + 1)]
        self.logger.debug(f"Processing: {len(page_urls)} HubTraffic pages...")

        # We can use a simpler concurrency model here since the API is JSON and fast
        semaphore = asyncio.Semaphore(pages_concurrency)

        async def fetch_page(url):
            async with semaphore:
                try:
                    content = await get_html_content(core=self.core, url=url)
                    assert isinstance(content, str)
                    return extractor_hubtraffic(content)
                except Exception as e:
                    self.logger.error(f"Failed to fetch HubTraffic page {url}: {e}")
                    return []

        # Fetch all pages concurrently
        tasks = [fetch_page(url) for url in page_urls]
        for completed_task in asyncio.as_completed(tasks):
            video_data_list = await completed_task
            for data in video_data_list:
                # Create Video object with pre-parsed data
                video = Video(url=data["url"], core=self.core, api_data=data)
                yield await video.init()


def str_to_bool(val: str) -> bool:
    return val.lower() in ('yes', 'true', 't', '1')

def can_download(state: dict) -> bool:
    if state["limit"] is None:
        return True
    return state["downloaded"] < state["limit"]

async def _cli_download_video_generator(generator, args, no_title: bool, state: dict):
    async for video in generator:
        if not can_download(state): break
        
        if getattr(args, "id_as_title", False) and hasattr(video, "video_id"):
            final_path = os.path.join(args.output, f"{video.video_id}.mp4")
            no_title_arg = True
        else:
            final_path = args.output
            no_title_arg = no_title
            
        await video.ensure_html()
        await video.download(quality=args.quality, path=final_path, no_title=no_title_arg)
        state["downloaded"] += 1

async def _cli_process_url(client: Client, url: str, args, no_title: bool, state: dict):
    try:
        if "view_video.php" in url:
            if not can_download(state): return
            video = await client.get_video(url)
            
            if getattr(args, "id_as_title", False) and hasattr(video, "video_id"):
                final_path = os.path.join(args.output, f"{video.video_id}.mp4")
                no_title_arg = True
            else:
                final_path = args.output
                no_title_arg = no_title
                
            await video.ensure_html()
            await video.download(quality=args.quality, path=final_path, no_title=no_title_arg)
            state["downloaded"] += 1
            
        elif "/short/" in url:
            if not can_download(state): return
            short = await client.get_short(url)
            
            if getattr(args, "id_as_title", False) and hasattr(short, "video_id"):
                final_path = os.path.join(args.output, f"{short.video_id}.mp4")
                no_title_arg = True
            else:
                final_path = args.output
                no_title_arg = no_title
                
            await short.download(quality=args.quality, path=final_path, no_title=no_title_arg)
            state["downloaded"] += 1
            
        elif "/gif/" in url:
            if not can_download(state): return
            gif = await client.get_gif(url)
            await gif.download(path=args.output, no_title=no_title)
            state["downloaded"] += 1
            
        elif "/album/" in url:
            album = await client.get_album(url)
            async for photo in album.get_photos(pages=args.pages):
                if not can_download(state): break
                await album.download_photo(photo["download_url"], path=args.output)
                state["downloaded"] += 1
                
        else:
            if "/pornstar/" in url:
                obj = await client.get_pornstar(url)
            elif "/model/" in url:
                obj = await client.get_model(url)
            elif "/users/" in url:
                obj = await client.get_user(url)
            elif "/channels/" in url:
                obj = await client.get_channel(url)
            elif "/playlists/" in url:
                obj = await client.get_playlist(url)
            else:
                print(f"Unsupported or unrecognized URL format: {url}")
                return

            await _cli_download_video_generator(obj.get_videos(pages=args.pages), args, no_title, state)
                
    except Exception as e:
        print(f"Error processing {url}: {e}")

async def run_main():
    parser = argparse.ArgumentParser(description="PornHub API Command Line Interface")
    parser.add_argument("--download", metavar="URL (str)", type=str, help="URL to download from")
    parser.add_argument("--quality", metavar="best,half,worst", type=str, help="The video quality (best,half,worst)", required=True)
    parser.add_argument("--file", metavar="Source to .txt file", type=str, help="(Optional) Specify a file with URLs (separated with new lines)")
    parser.add_argument("--output", metavar="Output directory", type=str, help="The output path (with filename)", required=True)
    parser.add_argument("--no-title", metavar="True,False", type=str, help="Whether to apply video title automatically to output path or not", required=True)
    parser.add_argument("--pages", metavar="Pages (int)", type=int, default=1, help="Number of pages to fetch for iterables (Default: 1)")
    parser.add_argument("--email", type=str, help="Account email for login", default=None)
    parser.add_argument("--password", type=str, help="Account password for login", default=None)
    parser.add_argument("--id-as-title", action="store_true", help="Use the video ID as the output title")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of videos to download")
    parser.add_argument("--liked", action="store_true", help="Download liked/favorite videos (requires login)")
    parser.add_argument("--recommended", action="store_true", help="Download recommended videos (requires login)")
    parser.add_argument("--watched", action="store_true", help="Download watched/history videos (requires login)")

    args = parser.parse_args()
    no_title = str_to_bool(args.no_title)

    login = False
    client = Client(email=args.email, password=args.password, login=False)
    if args.email and args.password:
        login = True
        await client.login()

    urls = []
    if args.download:
        urls.append(args.download)

    if args.file:
        with open(args.file, "r") as file:
            content = file.read().splitlines()
            urls.extend(content)

    state = {"downloaded": 0, "limit": args.limit}

    for url in urls:
        await _cli_process_url(client, url, args, no_title, state)
        if not can_download(state):
            break

    if login:
        if getattr(args, "liked", False):
            await _cli_download_video_generator(client.get_favorites(pages=args.pages), args, no_title, state)
        if getattr(args, "recommended", False):
            await _cli_download_video_generator(client.get_recommended(pages=args.pages), args, no_title, state)
        if getattr(args, "watched", False):
            await _cli_download_video_generator(client.get_history(pages=args.pages), args, no_title, state)
    else:
        if getattr(args, "liked", False) or getattr(args, "recommended", False) or getattr(args, "watched", False):
            print("Warning: --liked, --recommended, and --watched require --email and --password to work. Skipping.")

def cli():
    asyncio.run(run_main())

if __name__ == "__main__":
    cli()
