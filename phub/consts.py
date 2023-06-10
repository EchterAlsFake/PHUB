'''
Constants for the PHUB package.
'''

import re
from typing import Self

from phub import utils


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

class Quality:
    '''
    Represents a custom quality.
    '''
    
    # Presets
    BEST = 'best'
    MIDDLE = 'middle'
    WORST = 'worst'
    
    def __new__(cls, value: str | int | Self) -> Self:
        '''
        Verify quality 
        '''
        
        assert isinstance(value, (str, int, Quality))
        
        # Error protection
        if isinstance(value, str) and value.lower() not in ('best', 'middle', 'worst'):
            raise ValueError('Invalid value (must be BEST, MIDDLE or WORST if string)')
        
        # Avoid something bad
        if isinstance(value, Quality): value = value.value
        
        return object.__new__(cls)
    
    def __init__(self, value: str | int | Self) -> None:
        '''
        Generate a new Quality object.
        '''
        
        self.value = value
        self.frozen = True
    
    def __setattr__(self, *_) -> None:
        '''
        Prevent user from modyfing class.
        '''
        
        if not getattr(self, 'frozen', 0): return super().__setattr__(*_)
        raise Exception('Quality class can\'t be modifed.')
    
    def __repr__(self) -> str:
        return f'<phub.Quality {self.value}>'
    
    def select(self, quals: dict) -> str:
        '''
        Make a choice among all possible qualities for a video.
        '''
        
        keys = list(quals.keys())
        
        if isinstance(self.value, str):
            # Get approximative quality
            
            if self.value == Quality.BEST: return quals[max(keys)]
            elif self.value == Quality.WORST: return quals[min(keys)]
            else: return quals[ keys[ len(keys) // 2 ] ]
        
        elif isinstance(self.value, int):
            # Get exact quality or nearest
            
            if (s:= str(self.value)) in keys: return quals[s]
            else: return quals[utils.closest(keys, self.value)]
        
        # This should not happen
        raise TypeError('Internal error: quality type is', type(self.value))

class regexes:
    '''
    Compiled regexes methods used for parsing.
    '''
    
    extract_token        = re.compile( r'token *?= \"(.*?)\",'                                                       ).findall   # Extract session token from the home page
    extract_videos       = re.compile( r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?title=\"(.*?)\"', re.DOTALL ).findall   # Extract videos from a page
    is_valid_video_url   = re.compile( r'https://.{2,3}\.pornhub\.com/view_video\.php\?viewkey=[a-z\d]{13,15}'       ).fullmatch # Verify video URL validity
    video_search_counter = re.compile( r'showingCounter\">.*? (\d+) +</',                                  re.DOTALL ).findall   # Extract video counter from research responses
    video_likes          = re.compile( r'span class=\"votes(Up|Down)\" data-rating.*?>(.*?)<'                        ).findall   # Extract likes from a video page
    video_interactions   = re.compile( r'interactionStatistic\": \[(.*?)\]',                               re.DOTALL ).findall   # Find interaction stats from a video page
    video_flashvar       = re.compile( r'var (flashvars_\d*) = ({.*});\n'                                            ).findall   # Video obfuscation script part
    sub_js_comments      = re.compile( r'\/\*.*?\*\/'                                                                ).sub       # Remove js comments
    sub_root             = re.compile( r'https://.{2,3}\.pornhub\.com/'                                              ).sub       # Substitue URL roots

# EOF