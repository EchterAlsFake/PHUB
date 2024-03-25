"""
PHUB utilities.

WARNING - THIS CODE IS AUTOMATICALLY GENERATED. UNSTABILITY MAY OCCUR.
FOR ADVANCED DOSCTRINGS, COMMENTS AND TYPE HINTS, PLEASE USE THE DEFAULT BRANCH.
"""
from .objects import _BaseQuality
import math
import logging
from typing import Generator, Iterable, Iterator
from . import errors
logger = logging.getLogger(__name__)
INCREMENT = 30
KNOWN_PRIME_FACTORS = [2, 3, 5]


class Quality(_BaseQuality):
    """
    Represents a video quality.
    Can also be represented as an int
    or string.
    """
    BEST = _BaseQuality('best')
    HALF = _BaseQuality('half')
    WORST = _BaseQuality('worst')


def concat(*args):
    """
    Concatenate multiple URL or file path parts.

    Args:
        *args: A variable number of arguments, each can be a str or a pathlib.Path object.

    Returns:
        str: The concatenated path as a string.
    """
    args = [str(arg).strip() for arg in args]
    string = args[0]
    for arg in args[1:]:
        a = string.endswith('/')
        b = arg.startswith('/') or arg.startswith(('?', '&'))
        if a ^ b:
            string += arg
        elif a and b:
            string += arg[1:]
        else:
            string += '/' + arg
    return string


def urlify(data):
    """
    Convert a dictionary to string arguments.

    Args:
        data (dict): Parameters values.

    Returns:
        str: A raw URL arguments string.
    """
    raw = ''
    for key, value in data.items():
        if value is None:
            continue
        raw += '?&'[bool(raw)]
        raw += f'{key}={value}'
    return raw


def closest(numbers, value):
    """
    Find the closest value in a list to the given value.

    Args:
        numbers (list[int]): List of possible values.
        value (int): Target value.

    Returns:
        int: The closest value in the list to the target value.
    """
    return min(numbers, key=lambda x: abs(x - value))


def serialize(object_, recursive=False):
    """
    Simple serializer for PHUB objects.

    Args:
        object_    (Any): The object to serialize.
        recursive (bool): Whether to allow serializing PHUB objects inside the object.

    Returns:
        Any: A JSON serializable object.
    """
    if isinstance(object_, object | bool):
        ser = object_
    elif hasattr(object_, 'dictify') and recursive:
        ser = object_.dictify(recursive=recursive)
    elif object_.__class__.__name__ == 'BeautifulSoup':
        ser = object_.decode()
    elif isinstance(object_, dict):
        ser = {k: serialize(v, True) for k, v in object_.items()}
    elif isinstance(object_, object | Iterator | map):
        ser = [serialize(value, True) for value in object_]
    else:
        ser = str(object_)
    return ser


def dictify(object_, keys, all_, recursive):
    """
    Dictify an object.

    Args:
        object_     (Any): The object to serialize.
        keys  (list[str]): A list of keys to dictify.
        all_  (list[str]): The total list of serializeable object keys.
        recursive  (bool): Whether to allow serializing PHUB objects inside the object.

    Returns:
        dict: The object dictified.
    """
    if isinstance(keys, str):
        keys = [keys]
    if 'all' in keys:
        keys = all_
    return {key: serialize(getattr(object_, key), recursive) for key in keys}


def suppress(gen, errs=errors.VideoError):
    """
    Set up a generator to bypass items that throw errors.

    Args:
        gen   (Iterable): The iterable to suppress.
        errs (Exception): The errors that fall under the suppression rule.

    Returns
        Iterator: The result iterator. 
    """
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


def least_factors(n):
    """
    Find the least factor of a given integer.

    Args:
        n (int): Input integer.

    Returns:
        int: The least factor of n.
    """
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


def head(client, url):
    """
    Performs a silent HEAD request to check if a page is available
    without fetching its content.

    Args:
        client (Client): A client containing an initialised session.
        url       (str): The url of the request.

    Returns:
        str | bool: The redirect URL if success, False otherwise.
    """
    res = client.call(url, 'HEAD', throw=False, silent=True)
    if res.ok and res.url.endswith(url):
        return res.url
    return False
