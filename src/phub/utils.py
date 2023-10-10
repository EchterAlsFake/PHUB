'''
PHUB utilities.
'''

import json
import requests

from . import consts, locals

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
    Convert a dictionnary to string arguments.
    
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

# EOF