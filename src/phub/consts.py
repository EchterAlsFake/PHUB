"""
PHUB constants.

WARNING - THIS CODE IS AUTOMATICALLY GENERATED. UNSTABILITY MAY OCCUR.
FOR ADVANCED DOSCTRINGS, COMMENTS AND TYPE HINTS, PLEASE USE THE DEFAULT BRANCH.
"""
import logging
import re as engine
from re import Pattern as p
from typing import Callable
from . import errors
logger = logging.getLogger(__name__)
HOST = 'https://www.pornhub.com/'
API_ROOT = HOST + 'webmasters/'
HEADERS = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en,en-US', 'Connection': 'keep-alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'}
COOKIES = {'accessAgeDisclaimerPH': '1', 'accessAgeDisclaimerUK': '1',
           'accessPH': '1', 'age_verified': '1', 'cookieBannerState': '1', 'platform': 'pc'}
LOGIN_PAYLOAD = {'from': 'pc_login_modal_:homepage_redesign'}
RSS = 'https://www.pornhub.com/video/webmasterss'
MAX_CALL_RETRIES = 4
MAX_CALL_TIMEOUT = 0.4
CALL_TIMEOUT = 30
CHALLENGE_TIMEOUT = 2
DOWNLOAD_SEGMENT_MAX_ATTEMPS = 5
DOWNLOAD_SEGMENT_ERROR_DELAY = 0.5
FFMPEG_EXECUTABLE = 'ffmpeg'
FFMPEG_COMMAND = FFMPEG_EXECUTABLE + \
    ' -i "{input}" -bsf:a aac_adtstoasc -y -c copy {output}'
IFRAME = '<iframe src="https://www.pornhub.com/embed/{key}" frameborder="0" width="{width}" height="{height}" scrolling="no" allowfullscreen></iframe>'
LANGUAGES = ['cn', 'de', 'fr', 'it', 'pt', 'pl', 'rt', 'nl', 'cz', 'jp']
FEED_CLASS_TO_CONST = {'stream_videos_uploaded': 'Section.VIDEO',
                       'stream_favourites_videos': 'Section.FAVORITE', 'stream_grouped_comments_videos': 'Section.COMMENT'}
WrappedRegex = Callable[[str, object], object]


def _throw_re_error(pattern):
    """
    Raises an error based on a pattern name.

    Args:
        pattern (str): The regex pattern.
    """
    regex_name = _REGEXES_NAMES.get(pattern) or f'Unknown ({pattern})'
    logger.error('Pattern <%s> failed', regex_name)
    raise errors.RegexError(f'Regex <{regex_name}> failed.')


def eval_flags(flags):
    """
    Evaluate flags.

    Args:
        flags (list[int]): List of flags arguments.

    Returns:
        int: The flag(s) value.
    """
    if len(flags):
        return flags[0]
    return 0


def find(*args):
    """
    Compile a single find regex and wraps handling its errors.

    Returns:
        Callable: Wrapped regex callable. If the second argument evaluates to False, it won't raise an error.
    """
    *flags, pattern = args
    flags = eval_flags(flags)
    regex = engine.compile(pattern, flags)

    def wrapper(string, throw=True):
        matches = regex.findall(string)
        if throw and (not matches):
            _throw_re_error(pattern)
        if len(matches):
            return matches[0]
    wrapper.__doc__ = pattern
    return wrapper


def mtch(*args):
    """
    Compile a regex specifically for finding the viewkey in a URL and wraps handling its errors.

    Returns:
        Callable: Wrapped regex callable for extracting viewkey. If the second argument evaluates to False, it won't raise an error.
    """
    *flags, pattern = args
    flags = eval_flags(flags)
    regex = engine.compile(pattern, flags)

    def wrapper(string, throw=True):
        match = regex.search(string)
        if match:
            return match.group(1)
        if throw:
            _throw_re_error(pattern)
    return wrapper


def comp(*args):
    """
    Compile a regex using a custom method with error handling.

    Returns:
        Callable: Wrapped regex callable.
    """
    *flags, method, pattern = args
    flags = eval_flags(flags)
    regex = engine.compile(pattern, flags)

    def wrapper(*args):
        try:
            matches = method(regex, *args)
            return matches
        except AttributeError:
            logger.error('Invalid regex method: \x1b[91m%s\x1b[0m', method)
            raise AttributeError('Invalid compiled regex method:', method)
        except Exception:
            _throw_re_error(pattern)
    return wrapper


def subc(*args):
    """
    Compile a substraction regex and apply its replacement to each call.

    Returns:
        Callable: Wrapped regex callable.
    """
    *flags, pattern, repl = args
    flags = eval_flags(flags)
    regex = engine.compile(pattern, flags)

    def wrapper(*args):
        try:
            return regex.sub(repl, *args)
        except Exception:
            _throw_re_error(pattern)
    return wrapper


class re:
    """
    API regexes.
    """
    _raw_root = 'https:\\/\\/.{2,3}\\.pornhub\\..{2,3}\\/'
    get_viewkey = mtch('[&\\?]viewkey=([a-z\\d]+)(?=&|$)')
    ffmpeg_line = find('seg-(\\d*?)-')
    get_flash = find('var (flashvars_\\d*) = ({.*});\\n')
    get_token = find('token *?= \\"(.*?)\\",')
    video_channel = find(
        'href=\\"(.*?)\\" data-event=\\"Video Underplayer\\".*?bolded\\">(.*?)<')
    video_model = find(
        'n class=\\"usernameBadgesWrapper.*? href=\\"(.*?)\\"  class=\\"bolded\\">(.*?)<')
    get_feed_type = find('data-table="(.*?)"')
    get_user_type = find('\\/(model|pornstar|channels|user|users)\\/.*?')
    get_thumb_id = find('\\/([a-z0-9]+?)\\/(?=original|thumb)')
    remove_host = subc(_raw_root, '')
    is_favorite = find('<div class=\\".*?js-favoriteBtn.*?active\\"')
    eval_video = find(
        engine.DOTALL, 'id=\\"(.*?)\\".*?-vkey=\\"(.*?)\\".*?title=\\"(.*?)\\".*?src=\\"(.*?)\\".*?-mediabook=\\"(.*?)\\".*?marker-overlays.*?>(.*?)</div')
    user_avatar = find(
        engine.DOTALL, 'previewAvatarPicture\\">.*?src=\\"(.*?)\\"')
    query_counter = find(
        engine.DOTALL, 'showing(?:Counter|Info).*?\\">.*?(\\d+)\\s*<\\/')
    user_bio = find(
        engine.DOTALL, '\\"aboutMeSection.*?\\"title.*?<div>\\s*(.*?)\\s*<\\/')
    container = find(engine.DOTALL, 'class=\\"container(.*)')
    document = find(engine.DOTALL, '.*')
    get_playlist_unavailable = find(engine.DOTALL, ': (\\d+)</h5')
    playlist_data = find(
        engine.DOTALL, 'id=\\"playlistWrapper(.*?)playlistSectionWrapper\\"')
    get_playlist_size = find(engine.DOTALL, '- (\\d+).*?\\"avatarPosition')
    get_playlist_likes = find(
        engine.DOTALL, '<span class="votesUp">(.*?)</span>')
    get_playlist_dislikes = find(
        engine.DOTALL, '<span class="votesDown">(.*?)</span>')
    get_playlist_ratings = find(
        engine.DOTALL, '<span class="percent">(.*?)%</span>')
    get_playlist_views = find(
        engine.DOTALL, '<span class="count">(.*?)</span>')
    get_playlist_title = find(engine.DOTALL, 'id="watchPlaylist.*?>(.*?)<')
    get_playlist_author = find(
        engine.DOTALL, 'data-type=\\"user.*?href=\\"(.*?)\\"')
    get_challenge = find(
        engine.DOTALL, 'go\\(\\).*?{(.*?)n=l.*?KEY.*?s\\+\\":(\\d+):')
    parse_challenge = subc(
        engine.DOTALL, '(?:var )|(?:/\\*.*?\\*/)|\\s|\\n|\\t|(?:n;)', '')
    ponct_challenge = subc(engine.DOTALL, '(if.*?&1\\)|else)', '\\1:')
    get_users = comp(engine.DOTALL, p.findall,
                     'userLink.*?=\\"(.*?)\\".*?src=\\"(.*?)\\"')
    user_infos = comp(engine.DOTALL, p.findall,
                      'infoPiece\\".*?span>\\s*(.*?):.*?smallInfo\\">\\s*(.*?)\\s*<\\/')
    feed_items = comp(engine.DOTALL, p.findall,
                      'feedItemSection\\"(.*?)<\\/section')
    get_ps = comp(engine.DOTALL, p.findall,
                  'img.*?src=\\"(.*?)\\".*?href=\\"(.*?)\\".*?>(.*?)<.*?(\\d.*?)\\s')
    get_videos = comp(engine.DOTALL, p.findall, '<li.*?videoblock(.*?)</li')
    get_markers = comp(engine.DOTALL, p.findall, 'class=\\"(.*?)\\"')
    get_urls = comp(p.findall, 'https:\\/\\/.*?(?:\\s|$)')
    get_playlist_tags = comp(p.findall, 'data-label=\\"tag.*?>(.*?)<')
    is_url = comp(p.fullmatch, 'https*:\\/\\/.*')
    is_video_url = comp(p.fullmatch, _raw_root +
                        'view_video\\.php\\?viewkey=(?:ph)?[a-z\\d]{3,}(&pkey=\\d+)?')
    is_quality = comp(p.fullmatch, '\\d+p?')
    is_playlist = comp(
        p.fullmatch, '^https?:\\/\\/(?:www\\.)?(?:[a-z]{2}\\.)?pornhub\\.[a-z]{2,3}\\/playlist\\/\\d+$')


_REGEXES_NAMES = {v.__doc__: k for k, v in vars(re).items() if v.__doc__}
