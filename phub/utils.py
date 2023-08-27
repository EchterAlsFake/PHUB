'''
PHUB 4 utilities.
'''

import math
import json
import requests

from . import consts
from . objects import data

def concat(*args: list[str]) -> str:
    '''
    Concatenate multiple url parts.
    '''
        
    args = [arg.strip('/') for arg in args]
    return '/'.join(args)

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
    return min(iter, key = difference)

def update_categories():
    '''
    Update the categories in the Category classes.
    
    Warning - This will make changes to phub.data.py.
    '''
    
    # TODO - refactor
    
    url = concat(consts.API_ROOT, 'categories')
    res = requests.get(url)
    res.raise_for_status()
    data_ = sorted(json.loads(res.text)['categories'],
                   key = lambda d: d['id'])
    
    with open(data.__file__, 'r') as file:
        content = file.read()
    
    # Format categories
    cats = ''
    for obj in data_:
        name = obj['category']
        var = name.upper().replace('-', '_').replace('/', '_').replace(' ', '_')
        
        if var[0].isdigit(): var = '_' + var
        
        cats += f'\n    {var: <21} = _BaseCategory( {obj["id"]: >3}, \'{name: <21}\' )'
    
    content = content.split('#@START-CATEGORY')[0] + \
              '#@START-CATEGORY' + \
              cats + '\n' + \
              '    #@END-CATEGORY' + \
              content.split('#@END-CATEGORY')[1]
    
    with open(data.__file__, 'w') as file:
        file.write(content)

# EOF