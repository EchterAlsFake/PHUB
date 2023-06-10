'''
Utilities for the PHUB package.
'''

from phub import consts
from string import ascii_letters

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
    return min(iter, key = difference)

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

# EOF