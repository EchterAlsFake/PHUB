'''
PHUB utilities.
'''

import math
import logging
import requests
from typing import Generator, Iterable, Iterator, Union

from . import errors
from . import consts

logger = logging.getLogger(__name__)

# Named constants for least_factors
INCREMENT = 30
KNOWN_PRIME_FACTORS = [2, 3, 5]


from .objects import _BaseQuality

class Quality(_BaseQuality):
    '''
    Represents a video quality.
    Can also be represented as an int
    or string.
    '''
    
    BEST  = _BaseQuality('best' )
    HALF  = _BaseQuality('half' )
    WORST = _BaseQuality('worst')


def concat(*args) -> str:
    '''
    Concatenate multiple URL or file path parts.

    Args:
        args: A variable number of arguments, each can be a str or a pathlib.Path object.

    Returns:
        str: The concatenated path as a string.
    '''

    # Convert all arguments to strings first
    args = [str(arg).strip() for arg in args]

    string = args[0]

    for arg in args[1:]:
        a = string.endswith('/')
        b = arg.startswith('/') or arg.startswith(('?', '&'))

        if a ^ b:
            string += arg  # 1 '/'
        elif a and b:
            string += arg[1:]  # 2 '/'
        else:
            string += '/' + arg  # 0 '/'

    return string


def urlify(data: dict) -> str:
    '''
    Convert a dictionary to string arguments.
    
    Args:
        data (dict): Parameters values.
    
    Returns:
        str: A raw URL arguments string.
    '''
    
    raw = ''

    for key, value in data.items():
        
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

def serialize(object_: object, recursive: bool = False) -> object:
    '''
    Simple serializer for PHUB objects.
    
    Args:
        object_ (Any): The object to serialize.
        recursive (bool): Whether to allow serializing PHUB objects inside the object.
    
    Returns:
        Any: A JSON serializable object.
    '''
    
    # if an object is a built-in
    if isinstance(object_, (str, int, float, bool)):
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
    elif isinstance(object_, (list, tuple, Generator, Iterator, map)):
        ser = [serialize(value, True) for value in object_]
    
    else:
        ser = str(object_)
    
    return ser

def dictify(object_: object,
            keys: Union[str, list[str]],
            all_: list[str],
            recursive: bool) -> dict:
    '''
    Dictify an object.
    
    Args:
        object_ (Any): The object to serialize.
        keys (list[str]): A list of keys to dictify.
        all_ (list[str]): The total list of serializeable object keys.
        recursive (bool): Whether to allow serializing PHUB objects inside the object.
    
    Returns:
        dict: The object dictified.
    '''
    
    if isinstance(keys, str): keys = [keys]
    if 'all' in keys: keys = all_
    
    return {key: serialize(getattr(object_, key), recursive)
            for key in keys}

def suppress(gen: Iterable, errs: Union[Exception, tuple[Exception]] = errors.VideoError) -> Iterator:
    '''
    Set up a generator to bypass items that throw errors.
    
    Args:
        gen (Iterable): The iterable to suppress.
        errs (Exception): The errors that fall under the suppression rule.
    
    Returns
        Iterator: The result iterator. 
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

def head(client: object, url: str) -> Union[str, bool]:
    '''
    Performs a silent HEAD request to check if a page is available
    without fetching its content.
    
    Args:
        client (Client): A client containing an initialised session.
        url (str): The url of the request.
    
    Returns:
        str | bool: The redirect URL if success, False otherwise.
    '''
    
    res: requests.Response = client.call(url, 'HEAD', throw = False, silent = True)
    
    # Make sure we were not redirected
    if res.is_success and not res.has_redirect_location:
        return res.url
    return False


def fix_url(url: str):
    """
    Changes a URL which includes the specific language site of PornHub to the default www.pornhub.com/org format,
    so that PornHub respects the accept-language header, so that we can apply our own custom language into the Client.

    Args:
        url: (str): The video URL to be changed

    Returns:
        str: The video URL without the language site.
    """

    for language, root_url in consts.LANGUAGE_MAPPING.items():
        if f"{language}.pornhub" in url:
            url = url.replace(language, "www", 1)
            return url

    return url  # Sometimes URL doesn't need to be changed. In this case, just return it.
