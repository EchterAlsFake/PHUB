import os
import sys
import time
from typing import Callable, Union

def progress(color: Union[dict, None] = dict(c1=30, c2=33, c3=34, c4=36), desc: str = 'Downloading') -> Callable:
    '''
    Simple progress display, with segment, percentage and speed display.
    
    Args:
        color (dict): ASCII progress colors.
        desc (str): Description to display.
    
    Returns:
        Callable: A wrapper to pass to a downloader.
    '''
    
    if not color: color = dict(c1='', c2='', c3='', c4='')
    
    color['c0'] = 0
    color = {k: '' if v == '' else f'\033[{v}m' for k, v in color.items()}
    
    tem = '\r{c1}' + desc + ' {c2}{percent}%{c0} - {c3}{cur}{c0}/{c3}{total}i{c0}' # ({c4}{speed}ips{c0})
    done = False
    start = time.time()
    
    def wrapper(cur: int, total: int) -> None:
        
        nonlocal done
        if done: return
        
        percent = round((cur / total) * 100)
        
        print(tem.format(percent = percent,
                         cur = cur,
                         total = total,
                         speed = round(cur // (time.time() - start), 1),
                         **color),
              end = '')
        
        if cur == total:
            done = True
            print()
    
    return wrapper

def bar(desc: str = 'Downloading', format_: str = ' |{bar}| [{cur}/{total}]') -> Callable:
    '''
    Simple progress bar, tqdm-like.
    
    Args:
        desc    (str): Bar description.
        format_ (str): Bar formatter.
    
    Returns:
        Callable: A wrapper to pass to a downloader.
    '''
    
    tem = desc + format_
    
    term_size = os.get_terminal_size().columns
    
    def wrapper(cur: int, total: int) -> None:

        raw = tem.format(cur = int(cur), total = int(total), bar = '{bar}')
        bar_length = term_size - len(tem) + 10
        percent = round((cur / total) * bar_length)
        
        print(raw.format(bar = ('=' * percent).ljust(bar_length, ' ')), end = '\r')
        
        if cur == total: print()
        
    return wrapper

def std(file = sys.stdout) -> Callable:
    '''
    Output to std.
    
    Args:
        file (TextIO): Output file.
    
    Returns:
        Callable: A wrapper to pass to a downloader.
    '''
    
    def wrapper(cur: int, total: int) -> None:
        print(round((cur / total) * 100), file = file)
    
    return wrapper

# Set default display
default = progress

# EOF