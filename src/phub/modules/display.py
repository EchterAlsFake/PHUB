import os
import sys
from typing import Callable

def progress(color: bool = True) -> Callable:
    '''
    Simple progress display.
    
    Args:
        color (bool): Wether to color the output using ANSI color codes.
    
    Returns:
        Callable: A wrapper to pass to a downloader.
    '''
    
    tem = '\rDownloading: {percent}% [{cur}/{total}]'
    
    if color:
        tem = '\rDownloading: \033[92m{percent}%\033[0m [\033[93m{cur}\033[0m/\033[93m{total}\033[0m]'
    
    def wrapper(cur: int, total: int) -> None:
        
        percent = round((cur / total) * 100)
        
        # print(tem.format(percent = percent, cur = cur, total = total))#, end = '\r') # TODO - glitches with ffmpeg download
        
        print(tem.format(percent = percent, cur = cur, total = total), end = '')
    
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
        
        raw = tem.format(cur = cur, total = total, bar = '{bar}')
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