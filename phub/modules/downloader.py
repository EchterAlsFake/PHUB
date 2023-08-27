'''
PHUB 4 download backends.
'''

from __future__ import annotations

import os
import time

import threading
from typing import TYPE_CHECKING, Generator, Callable

if TYPE_CHECKING:
    from ..core import Client

from .. import errors, consts

def _segment_wrap(client: Client,
                  url: str,
                  callback: Callable = None,
                  buffer: dict = None) -> bytes:
    '''
    Download a single segment.
    '''
    
    for _ in range(consts.DOWNLOAD_SEGMENT_MAX_ATTEMPS):
        
            segment = client.call(url, throw = False)
            
            if segment.ok:
                if buffer is not None:
                    buffer[url] = segment.content
                    callback()
                
                return segment.content

            print(url, 'thread failed, retrying in .05')
            time.sleep(1)
        
    raise errors.MaxRetriesExceeded(segment.status_code, segment.text)

def default(client: Client,
            segments: Generator,
            callback: Callable = None) -> bytes:
    '''
    Simple download.
    '''
    
    buffer = b''
    
    segments = list(segments)
    length = len(segments)
    
    for i, url in enumerate(segments):
        buffer += _segment_wrap(client, url)
        callback(i + 1, length)
    
    return buffer

def threaded(client: Client,
             segments: Generator,
             callback: Callable) -> bytes:
    '''
    Threaded download.
    '''
    
    buffer = {}
    finished = []
    
    def update():
        '''
        Called by threads on finish.
        '''
        
        nonlocal finished
        
        lb, lf = len(buffer), len(threads)
        
        callback(lb, lf)
        
        if lb >= lf:
            finished.append(True) # TODO crappy, refactor
    
    # Create the threads
    threads = [threading.Thread(target = _segment_wrap,
                                args = [client, url, buffer])
               for url in segments]
    
    print(f'Generated {len(threads)} threads')
    
    # Start the threads
    for thread in threads:
        time.sleep(.05)
        print('start')
        thread.start()
    
    # Wait for threads
    while len(buffer) < len(threads):
        print('DOWNLOAD', len(buffer))
        pass
    
    print('All finished')
    # Concatenate buffer
    video = b''
    
    for url in segments:
        video += buffer[url]
    
    print('COncatenated all')
    
    return video
        
        

def FFMPEG(client: Client, segments: Generator, callback) -> bytes:
    '''
    TODO
    '''
    
    # Write temp file
    with open('temp.m3u8', 'w') as file:
        for segment in segments:
            file.write(segment + '\n')
    
    # Call FFMPEG
    print('Starting ffmpeg')
    os.system('ffmpeg -i temp.m3u8 video.mp4')
    
    return b'none'

# EOF
    