'''
PHUB video download display presets.
'''

import tqdm

from typing import Callable

def progress(color: bool = True) -> Callable:
    '''
    Simple progress display.
    '''
    
    tem = 'Downloading: {percent}% [{cur}/{total}]'
    
    if color:
        tem = 'Downloading: \033[92m{percent}%\033[0m [\033[93m{cur}\033[0m/\033[93m{total}\033[0m]'
    
    def wrapper(cur: int, total: int) -> None:
        percent = round( (cur / total) * 100 )
    
        #print(tem.format(percent = percent, cur = cur, total = total),
        #    end = '\n' if percent >= 100 else '')
        
        print('\r' + tem.format(percent = percent, cur = cur, total = total), end = '')
            
    return wrapper

def bar(**kwargs) -> Callable:
    '''
    TQDM bar.
    '''
    
    pass # TODO

# Set default display
default = progress

# EOF