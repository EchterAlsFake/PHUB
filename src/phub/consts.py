'''
PHUB constants.
'''

import logging
import re as engine
from re import Pattern as p
from typing	import Callable

from . import errors

logger = logging.getLogger(__name__)


HOST = 'https://www.pornhub.com/'
API_ROOT = HOST + 'webmasters/'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,en-US',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'
}

LOGIN_PAYLOAD = {
    'from': 'pc_login_modal_:homepage_redesign',
}

RSS = 'https://www.pornhub.com/video/webmasterss'

MAX_CALL_RETRIES = 4 # Maximum times a HTTPError can be reproduced
MAX_CALL_TIMEOUT = .4 # Time to wait before retrying basic calls 

SEGMENT_LENGTH = 4 # Length of a PH video segment (in seconds)
MAX_VIDEO_RENEW_ATTEMPTS = 3
DOWNLOAD_SEGMENT_MAX_ATTEMPS = 5
DOWNLOAD_SEGMENT_ERROR_DELAY = .5

FFMPEG_EXECUTABLE = 'ffmpeg' # Use from PATH by default
FFMPEG_COMMAND = FFMPEG_EXECUTABLE + ' -i "{input}" -bsf:a aac_adtstoasc -y -c copy {output}'

IFRAME = '<iframe src="https://www.pornhub.com/embed/{key}" frameborder="0" width="{width}" height="{height}" scrolling="no" allowfullscreen></iframe>'

# Supported languages
LANGUAGES = [ 'cn', 'de', 'fr', 'it', 'pt', 'pl', 'rt', 'nl', 'cz', 'jp' ]

# Regex wrappers

WrappedRegex = Callable[[str, bool], str]

def eval_flags(flags: list[int]) -> int:
    '''
    Evaluate flags.
    
    Args:
        flags (list[int]): List of flags arguments.
    
    Returns:
        int: The flag(s) value.
    '''
    
    if len(flags):
        return flags[0]
    
    return 0

def find(*args) -> WrappedRegex:
    '''
    Compile a single find regex and wraps handling its errors.
    
    Returns:
        Callable: Wrapped regex callable. If the second argument evaluates to False, it won't raise an error.
    '''
    
    *flags, pattern = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)

    def wrapper(string: str, throw: bool = True):
        
        matches = regex.findall(string)
        if throw and not matches:
            logger.error('Pattern \033[91m%s\033[0m failed', pattern)
            raise errors.RegexError('Find regex failed.')
        
        if len(matches): return matches[0]
    
    return wrapper

def comp(*args) -> WrappedRegex:
    '''
    Compile a regex using a custom method with error handling.
    
    Returns:
        Callable: Wrapped regex callable.
    '''
    
    *flags, method, pattern = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)
    
    def wrapper(*args):
        
        try:
            matches = method(regex, *args)
            return matches
        
        except AttributeError:
            logger.error('Invalid regex method: \033[91m%s\033[0m', method)
            raise AttributeError('Invalid compiled regex method:', method)
    
    return wrapper

def subc(*args) -> WrappedRegex:
    '''
    Compile a substraction regex and apply its replacement to each call.
    
    Returns:
        Callable: Wrapped regex callable.
    '''
    
    *flags, pattern, repl = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)
    
    def wrapper(*args):
        
        try:
            return regex.sub(repl, *args)
        
        except Exception as err:
            logger.error('Pattern \033[91m%s\033[0m replacing \033[91m%s\033[0m failed', pattern, repl)
            raise errors.RegexError('Substraction failed:', err)
    
    return wrapper

class re:
    '''
    API regexes.
    '''
    
    _raw_root = r'https:\/\/.{2,3}\.pornhub\..{2,3}\/'
    
    # Find regexes
    ffmpeg_line   = find( r'seg-(\d*?)-'                                                                ) # Get FFMPEG segment progress
    get_flash     = find( r'var (flashvars_\d*) = ({.*});\n'                                            ) # Get flash data from a video page
    get_token     = find( r'token *?= \"(.*?)\",'                                                       ) # Get authentification token
    get_viewkey   = find(r'[&\?]viewkey=([a-z\d]{8,})(?=&|$)'                                           ) # Get video URL viewkey
    video_channel = find( r'href=\"(.*?)\" data-event=\"Video Underplayer\".*?bolded\">(.*?)<'          ) # Get video author, if channel
    video_model   = find( r'n class=\"usernameBadgesWrapper.*? href=\"(.*?)\"  class=\"bolded\">(.*?)<' ) # Get video author, if model
    get_feed_type = find( r'data-table="(.*?)"'                                                         ) # Get feed section type
    get_user_type = find( r'\/(model|pornstar|channels|user|users)\/.*?'                                ) # Get a user type
    user_avatar   = find( engine.DOTALL, r'previewAvatarPicture\">.*?src=\"(.*?)\"'                     ) # get the user avatar
    query_counter = find( engine.DOTALL, r'showing(?>Counter|Info).*?\">.*?(\d+)\s*<\/'                 ) # Get a query's video amount
    user_bio      = find( engine.DOTALL, r'\"aboutMeSection.*?\"title.*?<div>\s*(.*?)\s*<\/'            ) # Get the user bio
    container     = find( engine.DOTALL, r'class=\"container(.*)'                                       ) # Get the page container
    get_thumb_id  = find( r'\/([a-z0-9]+?)\/(?=original|thumb)'                                         ) # Get video id from its thumbnail 
    eval_video    = find( engine.DOTALL, r'id=\"(.*?)\".*?-vkey=\"(.*?)\".*?title=\"(.*?)\".*?src=\"(.*?)\".*?-mediabook=\"(.*?)\".*?marker-overlays.*?>(.*?)</div' ) # Parse video data
    
    # Findall regexess
    get_users   = comp( engine.DOTALL, p.findall, r'userLink.*?=\"(.*?)\".*?src=\"(.*?)\"'                                                   ) # Get all users while performing an advanced user search
    user_infos  = comp( engine.DOTALL, p.findall, r'infoPiece\".*?span>\s*(.*?):.*?smallInfo\">\s*(.*?)\s*<\/'                               ) # Get user info
    feed_items  = comp( engine.DOTALL, p.findall, r'feedItemSection\"(.*?)<\/section'                                                        ) # Get all items in the Feed
    get_ps      = comp( engine.DOTALL, p.findall, r'img.*?src=\"(.*?)\".*?href=\"(.*?)\".*?>(.*?)<.*?(\d.*?)\s'                              ) # Get all pornstars in a container (avatar, url, name, video count)
    get_videos  = comp( engine.DOTALL, p.findall, r'<li.*?videoblock(.*?)</li' ) # Get all videos
    get_markers = comp( engine.DOTALL, p.findall, r'class=\"(.*?)\"' ) # Get markers identifiers
    
    # Substraction regexes
    remove_host = subc( _raw_root, '' ) # Remove the HOST root from a URL
    
    # Verification regexes
    is_url       = comp( p.fullmatch, r'https*:\/\/.*'                                    ) # Check if a string is a URL
    is_video_url = comp( p.fullmatch, _raw_root + r'view_video\.php\?viewkey=[a-z\d]{8,}' ) # Check if a string is a video URL
    is_quality   = comp( p.fullmatch, r'\d+p?'                                            ) # Check if a string is a video quality (e.g. 144p)
    is_favorite  = find( r'<div class=\".*?js-favoriteBtn.*?active\"'                     ) # Check if a video is favorite
    
    # Challenge regexes
    get_challenge   = find( engine.DOTALL, r'go\(\).*?{(.*?)n=l.*?RNKEY.*?s\+\":(\d+):' )
    parse_challenge = subc( engine.DOTALL, r'(?:var )|(?:/\*.*?\*/)|\s|\n|\t|(?:n;)', '' )
    ponct_challenge = subc( engine.DOTALL, r'(if.*?&1\)|else)', r'\1:' )
    
    # feed item user = .*?userLink.*?href=\"(.*?)\"

# EOF