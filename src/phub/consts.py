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

SEGMENT_LENGTH = 4 # Length of a PH video segment
MAX_VIDEO_RENEW_ATTEMPTS = 3
DOWNLOAD_SEGMENT_MAX_ATTEMPS = 5
DOWNLOAD_SEGMENT_ERROR_DELAY = .5

FFMPEG_EXECUTABLE = 'ffmpeg' # Use from PATH by default
FFMPEG_COMMAND = FFMPEG_EXECUTABLE + ' -i "{input}" -bsf:a aac_adtstoasc -y -c copy {output}'


# Regex wrappers

def find(pattern: str, flags: engine.RegexFlag = 0) -> Callable[[str, bool], str]:
    '''
    Compile a single find regex and wraps handling its errors.
    '''
    
    regex = engine.compile(pattern, flags)

    def wrapper(string: str, throw: bool = True):
        
        matches = regex.findall(string)
        if throw and not matches:
            logger.error('Pattern %s failed', pattern)
            raise errors.RegexError('Find regex failed.')
        
        if len(matches): return matches[0]
    
    return wrapper

def comp(method: Callable, pattern: str, flags: int = 0) -> Callable[[str], str]:
    '''
    Compile a regex using a custom method with error handling.
    '''
    
    regex = engine.compile(pattern, flags)
    
    def wrapper(*args):
        
        try:
            matches = method(regex, *args)
            return matches
        
        except AttributeError:
            logger.error('Invalid regex method: %s', method)
            raise AttributeError('Invalid compiled regex method:', method)
    
    return wrapper

def subc(pattern: str, repl: str, flags: int = 0) -> Callable[[str], str]:
    '''
    Compile a substraction regex and apply its replacement to each call.
    '''
    
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
    Web scraping regexes.
    '''
    
    # Basic regexes
    get_token     = find( r'token *?= \"(.*?)\",'       )
    get_viewkey   = find( r'[&\?]viewkey=([a-z\d]{8,})' )
    is_video_url  = comp( p.fullmatch, r'https:\/\/.{2,3}\.pornhub\..{2,3}\/view_video\.php\?viewkey=[a-z\d]{8,}' )
    get_videos    = comp( p.findall, r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?data-action=\"(.*?)\".*?title=\"(.*?)\"', engine.DOTALL )
    is_url        = comp( p.fullmatch, r'https*:\/\/.*' )
    remove_host   = subc( r'https://.{2,3}\.pornhub\..{2,3}/', '' )
    
    # Resolve regexes
    get_flash     = find( r'var (flashvars_\d*) = ({.*});\n' )
    rm_comments   = subc( r'\/\*.*?\*\/', ''                 )
    
    # Find author regexes
    video_channel = find( r'href=\"(.*?)\" data-event=\"Video Underplayer\".*?bolded\">(.*?)<' )
    video_model   = find( r'n class=\"usernameBadgesWrapper.*? href=\"(.*?)\"  class=\"bolded\">(.*?)<' )

    # User regexes
    user_bio      = find( r'\"aboutMeSection.*?\"title.*?<div>\s*(.*?)\s*<\/', engine.DOTALL )
    user_infos    = comp( p.findall, r'infoPiece\".*?span>\s*(.*?):.*?smallInfo\">\s*(.*?)\s*<\/', engine.DOTALL )
    
    # Feed regexes
    feed_items    = comp( p.findall, r'feedItemSection\".*?userLink.*?href=\"(.*?)\".*?feedInfo\">(.*?)<\/section', engine.DOTALL )
    
    ffmpeg_line   = find( r'seg-(\d*?)-' )

# EOF