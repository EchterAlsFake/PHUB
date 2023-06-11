'''
Utilities for the PHUB package.
'''

import sys
from string import ascii_letters

from typing import Callable
from datetime import datetime

from phub import consts

# Debug settings
DEBUG = False
DEBUG_LEVELS = list(range( 100, 108 ))
DEBUG_OVERRIDE: Callable[[str, str], None] = None
DEBUG_RESET: bool = False
DEBUG_FILE = sys.stdout

def slash(string: str, form: str) -> str:
    '''
    Properly add or remove trailling slashes
    from an URL.
    '''
    
    assert isinstance(string, str)
    assert isinstance(form, str)
    assert len(form) == 2
    
    start, end = form.replace('*', ' ')
    return (start + string.strip('/') + end).strip()

def shortify(string: str, max: int = 100) -> str:
    '''
    Shorten a string for display purposes.
    '''
    
    assert isinstance(max, int)
    assert isinstance(string, str)
    
    # Does nothing if string is short enough
    if len(string) < max: return string
    
    # Cut string
    return (string.replace('\n', ' ' * 4) + ' ' * max)[:max] + '...'

def basic(string: str, inc: bool) -> str:
    '''
    Set or remove URL root from an absolute or
    relative URL.
    '''
    
    assert isinstance(string, str)
    assert isinstance(inc, (bool, int))
    
    rel = consts.regexes.sub_root('', string)
    return ('', consts.ROOT)[inc] + rel

def closest(iter: list[int], value: int) -> int:
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    '''
    
    difference = lambda input_list: abs(input_list - value)
    response = min(iter, key = difference)
    log('utils', f'Selecting closest value to {value}: {response}', level = 3)
    return response

def extract_urls(string: str) -> list[str]:
    '''
    Extract URLs from a M3U file.
    '''
    
    return [line for line in string.split('\n')
            if line and not line.startswith('#')]

def pathify(string: str) -> str:
    '''
    Modify a string to be URL or path compatible.
    '''
    
    return ''.join(c for c in string if c in ascii_letters + '- _()')

def remove_video_ads(li: list) -> list:
    '''
    Remove trailling recommended videos from
    some playlists.
    '''
    
    return li[4:]

def log(cls: str, *text, level: int = 1, r: bool = False) -> None:
    '''
    Homemade logging.
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

# EOFs