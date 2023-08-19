'''
Constants for the PHUB package.
'''

import re

ROOT = 'https://www.pornhub.com/'

HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'
}

DEFAULT_REDIRECT = 'DCjQAI4yvwCP1m1jWvL-pYSJMPe24nneX--Jo4aA_qxPhXRHSH8_EDXajySaoBRh' # Idk what this is but we need it

LOGIN_PAYLOAD = {
    'redirect': DEFAULT_REDIRECT,
    'user_id': '',
    'intended_action': '',
    'from': 'pc_login_modal_:homepage_redesign',
    'taste_profile': ''
}

SEARCH_SORT_TRANSLATION = {
    'most relevant': None,
    'most recent': 'mr',
    'most viewed': 'mv',
    'top rated': 'tr',
    'longest': 'lg',
    None: None
}

class regexes:
    '''
    Compiled regexes methods used for parsing.
    '''
    
    # Extraction regexes
    extract_token        = re.compile( r'token *?= \"(.*?)\",'                                                       ).findall   # Extract session token from the home page
    extract_videos       = re.compile( r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?title=\"(.*?)\"', re.DOTALL ).findall   # Extract videos from a page
    extract_video_date   = re.compile( r'\"uploadDate\": \"(.*?)\"'                                                  ).findall   # Extract video publish date
    
    # Searching regexes
    video_search_counter = re.compile( r'showing(?>Counter|Info).*?\">.*?(\d+)\s*<\/',                     re.DOTALL ).findall   # Extract video counter from search responses
    video_likes          = re.compile( r'span class=\"votes(Up|Down)\" data-rating.*?>(.*?)<'                        ).findall   # Extract likes from a video page
    video_interactions   = re.compile( r'interactionStatistic\": \[(.*?)\]',                               re.DOTALL ).findall   # Find interaction stats from a video page
    video_flashvar       = re.compile( r'var (flashvars_\d*) = ({.*});\n'                                            ).findall   # Video obfuscation script part
    video_datalayer      = re.compile( r'window\.dataLayer\.push\(({.*?})\);',                             re.DOTALL ).findall   # Get video advanced datalayer
    video_channel        = re.compile( r'href=\"(.*?)\" data-event=\"Video Underplayer\".*?bolded\">(.*?)<'          ).findall   # Get video author if channel
    video_model          = re.compile( r'n class=\"usernameBadgesWrapper.*? href=\"(.*?)\"  class=\"bolded\">(.*?)<' ).findall   # Get video author if model
    
    video_renew_connect  = re.compile( r'<!--(.*?);\n{ doc.*?s\+"(.*?);',                                  re.DOTALL ).findall   # Find all infos to build renewing conn cookie
    
    # Substraction regexes
    sub_js_comments      = re.compile( r'\/\*.*?\*\/'                                                                ).sub       # Remove js comments
    sub_root             = re.compile( r'https://.{2,3}\.pornhub\.com/'                                              ).sub       # Substitue URL roots
    
    # Match regexes
    is_valid_video_url   = re.compile( r'https:\/\/.{2,3}\.pornhub\..{2,3}\/view_video\.php\?viewkey=[a-z\d]{8,}'    ).fullmatch # Verify video URL validity
    
    # Renew regexes
    class renew:
        script           = re.compile( r'go\(\) \{(.*?)n=least',                                           re.DOTALL ).findall   # Find renew script
        comment          = re.compile( r'\/\*.*?\*\/',                                                     re.DOTALL ).sub       # Remove JS comments
        states1          = re.compile( r'(if\s\(.*?&\s\d+\))'                                                        ).sub       # Format 'if' statements
        states2          = re.compile( r'(else)'                                                                     ).sub       # Format 'else' statements
        variables        = re.compile( r'var(.)=(\d+);'                                                              ).sub       # Remove variables leywords
        cookie_end       = re.compile( r'cookie.*?s\+\":(.*?);'                                                      ).findall   # Find cookie end string

class FeedType:
    '''
    Types representation (most) feed elements.
    '''
    
    SUBSCRIBED  = 'stream_subscriptions_pornstars'
    ACHIEVEMENT = 'stream_achievements'
    UPLOAD      = 'stream_videos_uploaded'
    SITE_UPLOAD = 'stream_sites_subscriptions'
    COMMENTED   = 'stream_grouped_comments_videos'
    # TODO more stream types


class locals:
    '''
    Locales constants.
    '''
    
    # Search production types
    PROFESSIONAL = 'professional'
    HOMEMADE = 'homemade'
    
    # Search sort filters
    MOST_RELEVANT = None
    MOST_RECENT = 'most recent'
    MOST_VIEWED = 'most viewed'
    TOP_RATED = 'top rated'
    LONGEST = 'longest'
    
    # Search time filters
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

# Exceptions

class CounterNotFound(Exception):
    '''
    The video counter wasn't found in the query,
    or is badly parsed.
    '''
    
    pass

class ParsingError(Exception):
    '''
    The parser failed to properly resolve the script
    for this element.
    '''
    
    pass

class UserNotFoundError(Exception):
    '''
    Failed to find a PH user account.
    '''
    
    pass

class NotLoggedIn(Exception):
    '''
    The client is not logged to a PH account,
    but tried to access account data.
    '''

class AlreadyLoggedIn(Exception):
    '''
    The client already established a connection with PH.
    '''

class LogginFailed(Exception):
    '''
    Login phase failed. Credentials may be wrong.
    '''

class TooManyRequests(Exception):
    '''
    The client sent too many requests.
    To bypass, consider using proxies or
    set a small delay to the client request:
    
    .. code-block:: python
    
        client = phub.Client(delay = True)
    '''

class Noresult(Exception):
    '''
    The search query did not found videos with
    its given filters.
    '''

# EOF
