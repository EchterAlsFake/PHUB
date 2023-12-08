'''
PHUB utilities.
'''

import math
import json
import logging
import requests
from typing import Generator, Iterable

from . import consts, locals, errors

logger = logging.getLogger(__name__)

# Named constants for least_factors
INCREMENT = 30
KNOWN_PRIME_FACTORS = [2, 3, 5]


def concat(*args: list[str]) -> str:
    '''
    Concatenate multiple URL parts.
    
    Returns:
        str: The concatenated path.
    '''
    
    string: str = args[0].strip()
        
    for arg in args[1:]:
        arg = arg.strip()
        a = string.endswith('/')
        b = arg.startswith('/')
        
        if a ^ b:     string += arg       # 1 '/'
        elif a and b: string += arg[1:]   # 2 '/'
        else:         string += '/' + arg # 0 '/'
    
    return string

def urlify(dict_: dict) -> str:
    '''
    Convert a dictionary to string arguments.
    
    Args:
        dict_ (dict): Parameters values.
    
    Returns:
        str: A raw URL arguments string.
    '''
    
    raw = ''

    for key, value in dict_.items():
        
        if value is None: continue
        
        raw += '?&'[bool(raw)]
        raw += f'{key}={value}'
    
    return raw

def closest(numbers: list[int], value: int) -> int:
    '''
    Find the closest value in a list to the given value.

    Args:
        numbers (list[int]): List of possible values.
        value (int): Target value.

    Returns:
        int: The closest value in the list to the target value.
    '''
    
    return min(numbers, key = lambda x: abs(x - value))

def make_constant(string: str) -> str:
    '''
    Format the name of a variable to be a valid
    python constant.
    
    Args:
        string (str): The variable name.
    
    Returns:
        str: A python compatible constant name.
    '''
    
    var_name = string.upper() \
               .replace('-', '_') \
               .replace('/', '_') \
               .replace(' ', '_')

    if var_name[0].isdigit():
        var_name = '_' + var_name
    
    return var_name

def update_locals() -> None:
    '''
    Update the locals.

    Warning: This will modify phub.locals.py.
    '''
    
    # TODO - Refactor
    
    url = concat(consts.API_ROOT, 'categories')
    response = requests.get(url, timeout = 30)
    response.raise_for_status()

    sorted_categories = sorted(
        json.loads(response.text)['categories'],
        key = lambda d: d['id']
    )
    
    max_length = len(sorted(sorted_categories,
                            key = lambda d: len(d['category']))[-1]['category'])
    
    categories_str = ''
    for obj in sorted_categories:
        name = obj['category']
        var_name = make_constant(name)
        name = f'{obj["id"]}@{name}\''
        
        categories_str += f'\n    {var_name: <21} = Param( \'category\', \'{name: <{max_length + 1}}, reverse = True)'

    start_tag = '#START@CATEGORIES'
    end_tag = '#END@CATEGORIES'

    with open(locals.__file__, 'r+', encoding = 'utf-8') as file:
        content = file.read()
        content = content.split(start_tag)[0] + start_tag + \
                  categories_str + '\n' + '    ' + end_tag + \
                  content.split(end_tag)[1]

        file.seek(0)
        file.write(content)
        file.truncate()

def serialize(object_: object, recursive: bool = False) -> object:
    '''
    Simple serializer for PHUB objects.
    '''
    
    # if an object is a built-in
    if isinstance(object_, str | int | float | bool):
        ser = object_
    
    # If an object is a PHUB object
    elif hasattr(object_, 'dictify') and recursive:
        ser = object_.dictify(recursive = recursive)
    
    # If an object is a soup
    elif object_.__class__.__name__ == 'BeautifulSoup':
        ser = object_.decode()
    
    # If an object is a dict
    elif isinstance(object_, dict):
        ser = {k: (serialize(v, True)) for k, v in object_.items()}
    
    # If an object is a list or a generator
    elif isinstance(object_, list | tuple | Generator | map):
        ser = [serialize(value, True) for value in object_]
    
    else:
        ser = str(object_)
    
    return ser

def dictify(object_: object,
            keys: str | list[str],
            all_: list[str],
            recursive: bool) -> dict:
    '''
    Dictify an object.
    '''
    
    if isinstance(keys, str): keys = [keys]
    if 'all' in keys: keys = all_
    
    return {key: serialize(getattr(object_, key), recursive)
            for key in keys}

def suppress(gen: Iterable, errs: Exception | tuple[Exception] = errors.VideoError) -> Generator:
    '''
    Set up a generator to bypass items that throw errors.
    
    Args:
        gen: The iterable to suppress.
        errs: The errors that fall under the suppression rule.
    
    Returns
        Generator: The result generator. 
    '''
    
    logger.info('Initialising suppressed generator')
    iterator = iter(gen)
    
    while 1:
        try:
            item = next(iterator)
            yield item
        
        except StopIteration:
            break
        
        except Exception as err:
            if isinstance(err, errs):
                logger.warn('Suppressing error %s: %s', err, repr(err))
                continue
            
            raise err

def least_factors(n: int) -> int:
    '''
    Find the least factor of a given integer.

    Args:
        n (int): Input integer.

    Returns:
        int: The least factor of n.
    '''
    
    if n == 0:
        return 0

    if n % 1 or n * n < 2:
        return 1

    for factor in KNOWN_PRIME_FACTORS:
        if n % factor == 0:
            return factor

    sqrt_n = int(math.sqrt(n))
    i = 7

    while i <= sqrt_n:
        if n % i == 0:
            return i

        for offset in [4, 6, 10, 12, 16, 22, 24]:
            if n % (i + offset) == 0:
                return i + offset

        i += INCREMENT

    return n

# EOF