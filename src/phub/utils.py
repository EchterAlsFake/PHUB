'''
Utilities for the PHUB package.
'''

import sys
from string import ascii_letters

import math
import tqdm

from datetime import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Self, Literal

from phub import consts

# Debug settings
DEBUG = False
DEBUG_LEVELS = (None, 101, 103, 105, 104, 102, 107)
DEBUG_OVERRIDE: Callable[[str, str], None] = None
DEBUG_RESET: bool = False
DEBUG_FILE = sys.stdout

# === Utilities function === #

def slash(string: str, form: Literal['**', '*/', '/*', '//']) -> str:
    '''
    Properly add or remove trailling slashes from an URL.
    
    Slash templates examples:
    `**` -> No slash
    `//` -> Both slashes
    `/*` -> Start slash and not end slash
    `*/` -> End slash and not start slash
    
    Args:
        string: The string to transform.
        form: Slash template.
        
    Returns:
        str: The formated URL.
    '''
    
    assert isinstance(string, str)
    assert isinstance(form, str)
    assert len(form) == 2
    
    start, end = form.replace('*', ' ')
    return (start + string.strip('/') + end).strip()

def shortify(string: str, max: int = 180) -> str:
    '''
    Shorten a string for display purposes.
    
    Args:
        string (str): The string to shorten.
        max (int): Maximum string length.
    
    Returns the shorten string.
    '''
    
    assert isinstance(max, int)
    assert isinstance(string, str)
    
    # Does nothing if string is short enough
    if len(string) < max: return string
    
    # Cut string
    return (string.replace('\n', ' ' * 4) + ' ' * max)[:max] + '...'

def basic(string: str, inc: bool) -> str:
    '''
    Set or remove root from an URL.
    
    Args:
        string (str): The URL.
        inc (bool): Wether to add or remove the root.
    
    Returns:
        str: The formated URL. 
    '''
    
    assert isinstance(string, str)
    assert isinstance(inc, (bool, int))
    
    rel = consts.regexes.sub_root('', string)
    return ('', consts.ROOT)[inc] + rel

def closest(iter: list[int], value: int) -> int:
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    
    Args:
        iter (list[int]): List of possible values.
        value (int): Value to pick closest to.
    
    Returns:
        int: _description_
    '''
    
    difference = lambda input_list: abs(input_list - value)
    response = min(iter, key = difference)
    log('utils', f'Selecting closest value to {value}: {response}', level = 5)
    return response

def extract_urls(string: str) -> list[str]:
    '''
    Extract URLs from a M3U file.
    
    Args:
        string (str): The raw file content.
    
    Returns:
        list[str]: _description_
    '''
    
    return [line for line in string.split('\n')
            if line and not line.startswith('#')]

def pathify(string: str) -> str:
    '''
    Set a string to be path safe.
    
    Args:
        string: The string.
    
    Returns:
        str: a path safe string.
    '''
    
    return ''.join(c for c in string if c in ascii_letters + '- _()')

def log(cls: str, *text, level: int = 1) -> None:
    '''
    Homemade logging.
    
    Args:
        cls (str): Calling class
        text: Log content.
        level (int): Log level.
        r (bool): Wether log is inline.
    '''
    
    global DEBUG_RESET
    
    if not DEBUG: return
    
    text = ' '.join(map(str, text))
    
    if DEBUG_OVERRIDE: DEBUG_OVERRIDE(cls, text, level)
    
    color = DEBUG_LEVELS[level]
    date = datetime.now().strftime('%H:%M:%S')
    
    raw = f'\033[30m{date}\033[0m \033[{color}m {cls.upper(): ^10} \033[0m {text}'
    
    print(raw, file = DEBUG_FILE)

def hard_strip(text: str, sep: str = ' ') -> str:
    '''
    Remove all useless spaces from a text.
    
    Args:
        text (str): The text to strip.
        sep (str): Separator between each words.
    
    Returns:
        str: A stripped version of text.
    '''
    
    if not text: return
    return sep.join(text.split())

def register_properties(cls):
    '''
    Register a class property as a
    ___properties__ attribute.
    
    Args:
        cls (object): The class to use.
    
    Returns:
        The modified class.
    '''
    
    cls.__properties__ = []
    
    for name, method in cls.__dict__.items():
        if isinstance(method, cached_property):
            cls.__properties__.append(name)
    
    return cls

def least_factors(n: int):
    '''
    Rewrite of the PH least_factor function.
    I don't know why it is like that, don't ask.
    
    Args:
        n (int): Function input
    
    Returns:
        int: Function output
    '''
    
    if not n: return 0
    
    if (n % 1 or n * n < 2): return 1
    
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    if n % 5 == 0: return 5
    
    m = math.sqrt(n)
    
    i = 7
    while i <= m:
        
        if n % i == 0: return i
        
        if n % (i + 4) == 0: return i + 4
        if n % (i + 6) == 0: return i + 6
        if n % (i + 10) == 0: return i + 10
        if n % (i + 12) == 0: return i + 12
        if n % (i + 16) == 0: return i + 16
        if n % (i + 22) == 0: return i + 22
        if n % (i + 24) == 0: return i + 24
        
        i += 30
    
    return n

# === Presets === #

class download_presets:
    '''
    Callback presets for displaying download progress.
    
    Presets, or any function that contain a '__wrapper__' wrapper
    will be initialised by `Video.download` when the download starts.
    This is mainly because some functions need initialisation, like
    tqdm functions, but in some cases we don't have a global context,
    so that's why there is 2 layers of wrappers.
    '''
    
    @staticmethod
    def progress(color: bool = True) -> Callable:
        '''
        Print current process on one line.
        '''
        
        def __wrapper__():
            
            tem = 'Downloading: {percent}% [{cur}/{total}]'
            if color:
                tem = 'Downloading: \033[92m{percent}%\033[0m [\033[93m{cur}\033[0m/\033[93m{total}\033[0m]'
            
            def wrapper(cur: int, total: int) -> None:
                percent = round( (cur / total) * 100 )
            
                print(tem.format(percent = percent, cur = cur, total = total),
                    end = '\n' if percent >= 100 else '')
            
            return wrapper
        
        return __wrapper__
    
    @staticmethod
    def bar(**kwargs) -> Callable:
        '''
        Display current progress as a tqdm bar.
        '''
        
        def __wrapper__():
        
            bar = tqdm.tqdm(**kwargs)
        
            def wrapper(current: int, total: int) -> None:
                
                bar.total = total
                bar.update(1)
                if current == total: bar.close()
                
            return wrapper
        
        return __wrapper__
        
    @staticmethod
    def std(file = sys.stdout) -> Callable:
        '''
        Output progress as percentage to a file.
        '''
        
        def __wrapper__():
            
            def wrapper(cur: int, total: int) -> None:
                print(round( (cur / total) * 100 ), file = file)
            
            return wrapper
        
        return __wrapper__

# === Dataclasses === #

@dataclass
class BaseQuality:
    
    value: Literal['best', 'half', 'worst'] | int | Self
    
    def __post_init__(self) -> None:
        '''
        Verify quality type and value.
        '''
        
        if isinstance(self.value, BaseQuality):
            self.value = self.value.value
        
        if isinstance(self.value, str):
            assert self.value.lower() in ('best', 'half', 'worst')
    
    def select(self, quals: dict) -> str:
        '''
        Select among a list of qualities.
        
        Args:
            quals (dict): A dict containing qualities and URLs.
        
        Returns:
            str: The chosen quality URL.
        '''
        
        keys = list(quals.keys())
        log('Quality', f'Selecting {self.value} among {keys}', level = 5)
        
        if isinstance(self.value, str):
            # Get approximative quality
            
            if self.value == 'best': return quals[max(keys)]
            elif self.value == 'worst': return quals[min(keys)]
            else: return quals[ sorted(keys)[ len(keys) // 2 ] ]
        
        elif isinstance(self.value, int):
            # Get exact quality or nearest
            
            if (s:= str(self.value)) in keys: return quals[s]
            else: return quals[closest(keys, self.value)]
        
        # This should not happen
        raise TypeError('Internal error: quality type is', type(self.value))

class BaseCategory:
    '''
    Represent one or multiple categories.
    '''
    
    def __init__(self, id: str | int, name: str) -> None:
        '''
        Initialise a new category.
        '''
        
        self.name = name
        self.id = str(id)
    
    def __repr__(self) -> str:
        
        return f'<phub.Category {self.name}>'
    
    def __str__(self) -> str:
        
        return self.id
    
    def __or__(self, __value: Self) -> Self:
        '''
        Concatenate two categories.
        '''

        return Category(f'{self.id}-{__value.id}',
                        f'{self.name} & {__value.name}')

# === Constant classes === #

class Quality(BaseQuality):
    '''
    Represents a video quality.
    '''
    
    BEST = BaseQuality('best')
    HALF = BaseQuality('half')
    WORST = BaseQuality('worst')

class Category(BaseCategory):
    '''
    Represents a search category.
    '''
    
    # NOTE - These are all categories provided by PH when making
    # search requests, but where the fuck are the missing ones 
    ASIAN              = BaseCategory( 1  , 'Asian'              )
    ORGY               = BaseCategory( 2  , 'Orgy'               )
    AMATEUR            = BaseCategory( 3  , 'Amateur'            )
    BIG_ASS            = BaseCategory( 4  , 'Big Ass'            )
    BABE               = BaseCategory( 5  , 'Babe'               )
    BBW                = BaseCategory( 6  , 'BBW'                )
    BIG_DICK           = BaseCategory( 7  , 'Big Dick'           )
    BIG_TITS           = BaseCategory( 8  , 'Big Tits'           )
    BLONDE             = BaseCategory( 9  , 'Blonde'             )
    BONDAGE            = BaseCategory( 10 , 'Bondage'            )
    BRUNETTE           = BaseCategory( 11 , 'Brunette'           )
    CELEBRITY          = BaseCategory( 12 , 'Celebrity'          )
    BLOWJOB            = BaseCategory( 13 , 'Blowjob'            )
    BUKKAKE            = BaseCategory( 14 , 'Bukkake'            )
    CREAMPIE           = BaseCategory( 15 , 'Creampie'           )
    CUMSHOT            = BaseCategory( 16 , 'Cumshot'            )
    EBONY              = BaseCategory( 17 , 'Ebony'              )
    FETISH             = BaseCategory( 18 , 'Fetish'             )
    FISTING            = BaseCategory( 19 , 'Fisting'            )
    HANDJOB            = BaseCategory( 20 , 'Handjob'            )
    HARDCORE           = BaseCategory( 21 , 'Hardcore'           )
    MASTURBATION       = BaseCategory( 22 , 'Masturbation'       )
    TOYS               = BaseCategory( 23 , 'Toys'               )
    PUBLIC             = BaseCategory( 24 , 'Public'             )
    INTERRACIAL        = BaseCategory( 25 , 'Interracial'        )
    LATINA             = BaseCategory( 26 , 'Latina'             )
    LESBIAN            = BaseCategory( 27 , 'Lesbian'            )
    MATURE             = BaseCategory( 28 , 'Mature'             )
    MILF               = BaseCategory( 29 , 'MILF'               )
    PORNSTAR           = BaseCategory( 30 , 'Pornstar'           )
    REALITY            = BaseCategory( 31 , 'Reality'            )
    ANAL               = BaseCategory( 35 , 'Anal'               )
    HENTAI             = BaseCategory( 36 , 'Hentai'             )
    TEEN               = BaseCategory( 37 , 'Teen (18+)'         )
    POV                = BaseCategory( 41 , 'POV'                )
    RED_HEAD           = BaseCategory( 42 , 'Red Head'           )
    VINTAGE            = BaseCategory( 43 , 'Vintage'            )
    PARTY              = BaseCategory( 53 , 'Party'              )
    COMPILATION        = BaseCategory( 57 , 'Compilation'        )
    SMALL_TITS         = BaseCategory( 59 , 'Small Tits'         )
    WEBCAM             = BaseCategory( 61 , 'Webcam'             )
    THREESOME          = BaseCategory( 65 , 'Threesome'          )
    ROUGH_SEX          = BaseCategory( 67 , 'Rough Sex'          )
    SQUIRT             = BaseCategory( 69 , 'Squirt'             )
    DP                 = BaseCategory( 72 , 'DP'                 )
    POPULAR_WITH_WOMEN = BaseCategory( 73 , 'Popular With Women' )
    BISEXUAL_MALE      = BaseCategory( 76 , 'Bisexual Male'      )
    MASSAGE            = BaseCategory( 78 , 'Massage'            )
    COLLEGE            = BaseCategory( 79 , 'College (18+)'      )
    GANGBANG           = BaseCategory( 80 , 'Gangbang'           )
    ROLE_PLAY          = BaseCategory( 81 , 'Role Play'          )
    TRANSGENDER        = BaseCategory( 83 , 'Transgender'        )
    CARTOON            = BaseCategory( 86 , 'Cartoon'            )
    SCHOOL             = BaseCategory( 88 , 'School (18+)'       )
    BABYSITTER         = BaseCategory( 89 , 'Babysitter (18+)'   )
    CASTING            = BaseCategory( 90 , 'Casting'            )
    SMOKING            = BaseCategory( 91 , 'Smoking'            )
    SOLO_MALE          = BaseCategory( 92 , 'Solo Male'          )
    FEET               = BaseCategory( 93 , 'Feet'               )
    FRENCH             = BaseCategory( 94 , 'French'             )
    GERMAN             = BaseCategory( 95 , 'German'             )
    BRITISH            = BaseCategory( 96 , 'British'            )
    ITALIAN            = BaseCategory( 97 , 'Italian'            )
    ARAB               = BaseCategory( 98 , 'Arab'               )
    RUSSIAN            = BaseCategory( 99 , 'Russian'            )
    CZECH              = BaseCategory( 100, 'Czech'              )
    INDIAN             = BaseCategory( 101, 'Indian'             )
    BRAZILIAN          = BaseCategory( 102, 'Brazilian'          )
    KOREAN             = BaseCategory( 103, 'Korean'             )
    VIRTUAL_REALITY    = BaseCategory( 104, 'Virtual Reality'    )
    FPS60              = BaseCategory( 105, '60FPS'              )
    JAPANESE           = BaseCategory( 111, 'Japanese'           )
    EXCLUSIVE          = BaseCategory( 115, 'Exclusive'          )
    MUSIC              = BaseCategory( 121, 'Music'              )
    PUSSY_LICKING      = BaseCategory( 131, 'Pussy Licking'      )
    VERIFIED_AMATEURS  = BaseCategory( 138, 'Verified Amateurs'  )
    VERIFIED_MODELS    = BaseCategory( 139, 'Verified Models'    )
    BEHIND_THE_SCENES  = BaseCategory( 141, 'Behind The Scenes'  )
    OLD_YOUNG          = BaseCategory( 181, 'Old/Young (18+)'    )
    PARODY             = BaseCategory( 201, 'Parody'             )
    PISSING            = BaseCategory( 211, 'Pissing'            )
    SFW                = BaseCategory( 221, 'SFW'                )
    COSPLAY            = BaseCategory( 241, 'Cosplay'            )
    CUCKOLD            = BaseCategory( 242, 'Cuckold'            )
    STEP_FANTASY       = BaseCategory( 444, 'Step Fantasy'       )
    VERIFIED_COUPLES   = BaseCategory( 482, 'Verified Couples'   )
    SOLO_FEMALE        = BaseCategory( 492, 'Solo Female'        )
    FEMALE_ORGASM      = BaseCategory( 502, 'Female Orgasm'      )
    MUSCULAR_MEN       = BaseCategory( 512, 'Muscular Men'       )
    ROMANTIC           = BaseCategory( 522, 'Romantic'           )
    TATTOOED_WOMEN     = BaseCategory( 562, 'Tattooed Women'     )
    TRANS_WITH_GIRL    = BaseCategory( 572, 'Trans With Girl'    )
    TRANS_WITH_GUY     = BaseCategory( 582, 'Trans With Guy'     )

# EOF