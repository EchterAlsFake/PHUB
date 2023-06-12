'''
### Constants for the PHUB package. ###
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

class regexes:
    '''
    Compiled regexes methods used for parsing.
    '''
    
    # Extraction regexes
    extract_token        = re.compile( r'token *?= \"(.*?)\",'                                                       ).findall   # Extract session token from the home page
    extract_videos       = re.compile( r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?title=\"(.*?)\"', re.DOTALL ).findall   # Extract videos from a page
    extract_video_date   = re.compile( r'\"uploadDate\": \"(.*?)\"'                                                  ).findall   # Extract video publish date
    
    # Searching regexes
    video_search_counter = re.compile( r'showingCounter\">.*? (\d+) +</',                                  re.DOTALL ).findall   # Extract video counter from research responses
    video_likes          = re.compile( r'span class=\"votes(Up|Down)\" data-rating.*?>(.*?)<'                        ).findall   # Extract likes from a video page
    video_interactions   = re.compile( r'interactionStatistic\": \[(.*?)\]',                               re.DOTALL ).findall   # Find interaction stats from a video page
    video_flashvar       = re.compile( r'var (flashvars_\d*) = ({.*});\n'                                            ).findall   # Video obfuscation script part
    video_datalayer      = re.compile( r'window\.dataLayer\.push\(({.*?})\);',                             re.DOTALL ).findall   # Get video advanced datalayer
    video_channel        = re.compile( r'href=\"(.*?)\" data-event=\"Video Underplayer\".*?bolded\">(.*?)<'          ).findall   # Get video author if channel
    video_model          = re.compile( r'n class=\"usernameBadgesWrapper.*? href=\"(.*?)\"  class=\"bolded\">(.*?)<' ).findall   # Get video author if model
    
    # Substraction regexes
    sub_js_comments      = re.compile( r'\/\*.*?\*\/'                                                                ).sub       # Remove js comments
    sub_root             = re.compile( r'https://.{2,3}\.pornhub\.com/'                                              ).sub       # Substitue URL roots
    
    # Match regexes
    is_valid_video_url   = re.compile( r'https://.{2,3}\.pornhub\.com/view_video\.php\?viewkey=[a-z\d]{13,15}'       ).fullmatch # Verify video URL validity
    
    # Old
    # video_model          = re.compile( r'<span class=\"usernameBadgesWrapper\"><a rel=\"\" href=\"(.*?)\"  class=\"bolded\">(.*?)</a>').findall # Get video author if model

# EOF
