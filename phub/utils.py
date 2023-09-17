"""
PHUB 4 utilities.
"""

import math
import json
import requests

from . import consts
from .objects import data

# Named constants for least_factors
INCREMENT = 30
KNOWN_PRIME_FACTORS = [2, 3, 5]


def concat(*args: list[str]) -> str:
    """
    Concatenate multiple URL parts.
    """
    args = [arg.strip('/') for arg in args]
    return '/'.join(args)


def least_factors(n: int) -> int:
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


def closest(numbers: list[int], value: int) -> int:
    """
    Find the closest value in a list to the given value.

    Args:
        numbers (list[int]): List of possible values.
        value (int): Target value.

    Returns:
        int: The closest value in the list to the target value.
    """
    difference = lambda x: abs(x - value)
    return min(numbers, key=difference)


def update_categories():
    """
    Update the categories in the Category classes.

    Warning: This will modify phub.data.py.
    """
    url = concat(consts.API_ROOT, 'categories')
    response = requests.get(url)
    response.raise_for_status()

    sorted_categories = sorted(
        json.loads(response.text)['categories'],
        key=lambda d: d['id']
    )

    categories_str = ''
    for obj in sorted_categories:
        name = obj['category']
        var_name = name.upper().replace('-', '_').replace('/', '_').replace(' ', '_')

        if var_name[0].isdigit():
            var_name = '_' + var_name

        categories_str += f'\n    {var_name: <21} = _BaseCategory( {obj["id"]: >3}, \'{name: <21}\' )'

    with open(data.__file__, 'r+') as file:
        content = file.read()
        content = content.split('#@START-CATEGORY')[0] + \
                  '#@START-CATEGORY' + \
                  categories_str + '\n' + \
                  '    #@END-CATEGORY' + \
                  content.split('#@END-CATEGORY')[1]

        file.seek(0)
        file.write(content)
        file.truncate()