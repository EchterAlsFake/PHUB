"""
PHUB 4 utilities.
"""

import math
import json
import requests

from . import consts, locals 


def concat(*args: list[str]) -> str:
    """
    Concatenate multiple URL parts.
    """
    
    args = [arg.strip('/') for arg in args]
    return '/'.join(args)


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


def update_locals():
    """
    Update the locals.

    Warning: This will modify phub.locals.py.
    """
    
    # TODO - Refactor
    
    url = concat(consts.API_ROOT, 'categories')
    response = requests.get(url)
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
        var_name = name.upper().replace('-', '_').replace('/', '_').replace(' ', '_')

        if var_name[0].isdigit():
            var_name = '_' + var_name

        name += '\''
        
        # categories_str += f'\n    {var_name: <21} = Param( {obj["id"]: >3}, \'{name: <{max_length + 1}})'
        categories_str += f'\n    {var_name: <21} = Param( \'category\', {obj["id"]: >3}, \'{name: <{max_length + 1}})'

    start_tag = '#START@CATEGORIES'
    end_tag = '#END@CATEGORIES'

    with open(locals.__file__, 'r+') as file:
        content = file.read()
        content = content.split(start_tag)[0] + start_tag + \
                  categories_str + '\n' + '    ' + end_tag + \
                  content.split(end_tag)[1]

        file.seek(0)
        file.write(content)
        file.truncate()

# EOF