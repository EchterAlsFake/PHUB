'''
PHUB 4 utilities.
'''

import math

from . import consts

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