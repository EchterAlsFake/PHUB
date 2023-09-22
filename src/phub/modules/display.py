'''
PHUB video download display presets.
'''

import os
import sys
from typing import Callable

def progress(color: bool = True) -> Callable:
    '''
    Simple progress display.
    '''
    
    tem = 'Downloading: {percent}% [{cur}/{total}]'
    
    if color:
        tem = 'Downloading: \033[92m{percent}%\033[0m [\033[93m{cur}\033[0m/\033[93m{total}\033[0m]'
    
    def wrapper(cur: int, total: int) -> None:
        
        percent = round((cur / total) * 100)
        print(tem.format(percent = percent, cur = cur, total = total))#, end = '\r') # TODO - glitches with ffmpeg download
            
    return wrapper

def bar(desc = 'Downloading', format_ = ' |{bar}| [{cur}/{total}]') -> Callable:
    '''
    Progress bar.
    '''
    
    tem = desc + format_
    
    term_size = os.get_terminal_size().columns
    
    def wrapper(cur: int, total: int) -> None:
        
        raw = tem.format(cur = cur, total = total, bar = '{bar}')
        bar_length = term_size - len(tem) + 10
        percent = round((cur / total) * bar_length)
        
        print(raw.format(bar = ('=' * percent).ljust(bar_length, ' ')), end = '\r')
        
        if cur == total: print()
        
    return wrapper

def std(file = sys.stdout) -> Callable:
    '''
    Output to std.
    '''
    
    def wrapper(cur: int, total: int) -> None:
        print(round((cur / total) * 100), file = file)
    
    return wrapper

# Set default display
default = progress

# EOF