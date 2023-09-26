'''
PHUB 4 constants.
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

SEGMENT_LENGTH = 4 # Length of a PH video segment (in seconds)
MAX_VIDEO_RENEW_ATTEMPTS = 3
DOWNLOAD_SEGMENT_MAX_ATTEMPS = 5
DOWNLOAD_SEGMENT_ERROR_DELAY = .5

FFMPEG_EXECUTABLE = 'ffmpeg' # Use from PATH by default
FFMPEG_COMMAND = FFMPEG_EXECUTABLE + ' -i "{input}" -bsf:a aac_adtstoasc -y -c copy {output}'

# Regex wrappers

def eval_flags(flags: list[int]) -> int:
    '''
    Evaluate flags.
    '''
    
    if len(flags):
        return flags[0]
    
    return 0

def find(*args) -> Callable[[str, bool], str]:
    '''
    Compile a single find regex and wraps handling its errors.
    '''
    
    *flags, pattern = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)

    def wrapper(string: str, throw: bool = True):
        
        matches = regex.findall(string)
        if throw and not matches:
            logger.error('Pattern %s failed', pattern)
            raise errors.RegexError('Find regex failed.')
        
        if len(matches): return matches[0]
    
    return wrapper

def comp(*args) -> Callable[[str], str]:
    '''
    Compile a regex using a custom method with error handling.
    '''
    
    *flags, method, pattern = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)
    
    def wrapper(*args):
        
        try:
            matches = method(regex, *args)
            return matches
        
        except AttributeError:
            logger.error('Invalid regex method: %s', method)
            raise AttributeError('Invalid compiled regex method:', method)
    
    return wrapper

def subc(*args) -> Callable[[str], str]:
    '''
    Compile a substraction regex and apply its replacement to each call.
    '''
    
    *flags, pattern, repl = args
    flags = eval_flags(flags)
    
    regex = engine.compile(pattern, flags)
    
    def wrapper(*args):
        
        try:
            return regex.sub(repl, *args)
        
        except Exception as err:
            logger.error('Pattern %s replacing %s failed', pattern, repl)
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
    get_viewkey   = find( r'[&\?]viewkey=([a-z\d]{8,})'                                                 ) # Get video URL viewkey
    video_channel = find( r'href=\"(.*?)\" data-event=\"Video Underplayer\".*?bolded\">(.*?)<'          ) # Get video author, if channel
    video_model   = find( r'n class=\"usernameBadgesWrapper.*? href=\"(.*?)\"  class=\"bolded\">(.*?)<' ) # Get video author, if model
    get_feed_type = find( r'data-table="(.*?)"' ) # Get feed section type
    
    query_counter = find( engine.DOTALL, r'showing(?>Counter|Info).*?\">.*?(\d+)\s*<\/'      ) # Get a query's video amount
    user_bio      = find( engine.DOTALL, r'\"aboutMeSection.*?\"title.*?<div>\s*(.*?)\s*<\/' ) # Get the user bio
    
    # Findall regexess
    get_users  = comp( engine.DOTALL, p.findall, r'userLink.*?=\"(.*?)\".*?src=\"(.*?)\"'                                                   ) # Get all users while performing an advanced user search
    user_infos = comp( engine.DOTALL, p.findall, r'infoPiece\".*?span>\s*(.*?):.*?smallInfo\">\s*(.*?)\s*<\/'                               ) # Get user info
    # feed_items = comp( engine.DOTALL, p.findall, r'feedItemSection\".*?userLink.*?href=\"(.*?)\".*?feedInfo\">(.*?)<\/section'            ) # Get all items in the Feed
    # feed_items = comp( engine.DOTALL, p.findall, r'feedItemSection\".*?userLink.*?href=\"(.*?)\"(.*?)<\/section'                            ) # Get all items in the Feed
    feed_items = comp( engine.DOTALL, p.findall, r'feedItemSection\"(.*?)<\/section'                            ) # Get all items in the Feed
    get_videos = comp( engine.DOTALL, p.findall, r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?data-action=\"(.*?)\".*?title=\"(.*?)\"' ) # Get all videos in a container (fetch their id, action type and title)
    
    # Subscration regexes
    remove_host = subc( _raw_root, '' ) # Remove the HOST root from a URL
    
    # Verification regexes
    is_url       = comp( p.fullmatch, r'https*:\/\/.*'                                    ) # Check if a string is a URL
    is_video_url = comp( p.fullmatch, _raw_root + r'view_video\.php\?viewkey=[a-z\d]{8,}' ) # Check if a string is a video URL

# EOF