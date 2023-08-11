'''
### Utilities for the PHUB package. ###
'''

import sys
from string import ascii_letters

import tqdm
from datetime import datetime
from typing import Callable, Self

from phub import consts

# Debug settings
DEBUG = False
DEBUG_LEVELS = list(range( 100, 108 ))
DEBUG_OVERRIDE: Callable[[str, str], None] = None
DEBUG_RESET: bool = False
DEBUG_FILE = sys.stdout


def slash(string: str, form: str) -> str:
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
    log('utils', f'Selecting closest value to {value}: {response}', level = 3)
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

def remove_video_ads(li: list) -> list:
    '''
    Remove leading video ads from playlists.
    
    Args:
        li (list): A list of video URLs.
    
    Returns:
        list: A sanitized list of video URLs.
    '''
    
    return li[4:]

def log(cls: str, *text, level: int = 1, r: bool = False) -> None:
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
    raw = f'\033[30m{date}\033[0m \033[{color}m {cls.upper()} \033[0m {text}'
    
    # TODO - Refactor
    if r and not DEBUG_RESET:
        print(raw, end = '', file = DEBUG_FILE)
        DEBUG_RESET = True
    
    elif r and DEBUG_RESET: print(f'\r{raw}', end = '', file = DEBUG_FILE)
    elif not r and DEBUG_RESET: print(f'\n{raw}', file = DEBUG_FILE)
    else: print(raw, file = DEBUG_FILE)

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


class Quality:
    '''
    Represents a custom quality, e.g.:
    
    ```python
    # Using constants
    Quality.BEST
    Quality.MIDDLE
    Quality.WORST
    
    # Using absolute value
    Quality(1080) # Represents closest to 1080p
    Quality('best') # Equivalent to Quality.BEST
    ```
    '''
    
    # Presets
    BEST = 'best'
    MIDDLE = 'middle'
    WORST = 'worst'
    
    def __new__(cls, value: str | int | Self) -> Self:
        '''
        Verify quality type.
        '''
        
        log('quals', 'Forging new quality:', value, level = 6)
        
        assert isinstance(value, (str, int, Quality)), 'Invalid raw quality type'
        
        # Error protection
        if isinstance(value, str) and value.lower() not in ('best', 'middle', 'worst'):
            raise ValueError('Invalid value (must be BEST, MIDDLE or WORST if string)')
        
        # Avoid something bad
        if isinstance(value, Quality): value = value.value
        
        return object.__new__(cls)
    
    def __init__(self, value: str | int | Self) -> None:
        '''
        Generate a new Quality object.
        
        Args:
            value (str | int | Quality): The value to create quality from.
        '''
        
        self.value = value
        self.frozen = True
    
    def __setattr__(self, *_) -> None:
        '''
        Prevent user from changing class attributes.
        '''
        
        if not getattr(self, 'frozen', 0): return super().__setattr__(*_)
        raise Exception('Quality class can\'t be modifed.')
    
    def __repr__(self) -> str:
        return f'<phub.Quality {self.value}>'
    
    def __str__(self) -> str:
        return str(self.value)
    
    def select(self, quals: dict) -> str:
        '''
        Select among a list of qualities.
        
        Args:
            quals (dict): A dict containing qualities and URLs.
        
        Returns:
            str: The chosen quality URL.
        '''
        
        keys = list(quals.keys())
        log('quals', f'Selecting {self.value} among {keys}', level = 6)
        
        if isinstance(self.value, str):
            # Get approximative quality
            
            if self.value == Quality.BEST.value: return quals[max(keys)]
            elif self.value == Quality.WORST.value: return quals[min(keys)]
            else: return quals[ sorted(keys)[ len(keys) // 2 ] ]
        
        elif isinstance(self.value, int):
            # Get exact quality or nearest
            
            if (s:= str(self.value)) in keys: return quals[s]
            else: return quals[closest(keys, self.value)]
        
        # This should not happen
        raise TypeError('Internal error: quality type is', type(self.value))


# Define presets as objects
Quality.BEST = Quality(Quality.BEST)
Quality.MIDDLE = Quality(Quality.MIDDLE)
Quality.WORST = Quality(Quality.WORST)

# EOF
