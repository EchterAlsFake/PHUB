'''
PHUB 4 download backends.
'''

from __future__ import annotations

import copy
import time

import requests
import threading
import subprocess

from typing import TYPE_CHECKING, Generator, Callable

if TYPE_CHECKING:
    from ..core import Client
    from ..objects import Video
    from ..locals import Quality

from .. import errors, consts


'''
default  => Download one segment at once and concatenate them
FFMPEG   => FFMPEG handles everything
threaded => Threaded download + concatenation
'''

def default(video: Video,
            quality: Quality,
            callback: Callable,
            path: str,
            start: int = 0) -> None:
    '''
    Dummy download. Can fail with slow speeds.
    '''
    
    buffer = b''
    
    segments = list(video.get_segments(quality))[start:]
    length = len(segments)
    
    # Fetch segments
    for i, url in enumerate(segments):
        for _ in range(consts.DOWNLOAD_SEGMENT_MAX_ATTEMPS):
        
            segment = video.client.call(url, throw = False, timeout = 4)
            
            if segment.ok:
                buffer += segment.content
                break

            print('Retrying download')
            time.sleep(consts.DOWNLOAD_SEGMENT_ERROR_DELAY)
                
        else:
            print('Timed out. Refreshing segments...')
            return default(video, quality, callback, i - 1)
            
            # raise errors.MaxRetriesExceeded(segment.status_code, segment.text)
        
        callback(i + 1, length)
    
    # Concatenate
    with open(path, 'wb') as file:
        file.write(buffer)

def FFMPEG(video: Video,
           quality: Quality,
           callback: Callable,
           path: str) -> None:
    '''
    Download using FFMPEG. It has to be installed to your system.
    You can override FFMPEG access with consts.FFMPEG_COMMAND
    '''
    
    M3U = video.get_M3U_URL(quality)
    
    # Estimate video segment count
    length = int(video.duration.total_seconds() // consts.SEGMENT_LENGTH)
    
    command = consts.FFMPEG_COMMAND.format(input = M3U, output = path)
    
    # Call FFMPEG
    proc = subprocess.Popen(command,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT,
                            universal_newlines = True)
    
    while 1:
        line = proc.stdout.readline()
        if proc.poll() != None: break
        
        if 'Opening \'https' in line and '/seg' in line:
            
            index = consts.re.ffmpeg_line(line)
            callback(int(index), length)

def _thread(req: requests.PreparedRequest,
            session: requests.Session,
            delay: float,
            buffer: dict = None,
            queue: list = None) -> bytes | None:
    '''
    Download a single segment.
    '''
    
    raw = session.send(req).content
    
    while b'<html>' in raw:
        
        # If request fails, put it back in todo
        if queue is not None:
            return queue.append(req)
        
        time.sleep(delay)
        raw = session.send(req).content
    
    else:
        if buffer is None: return raw
        buffer[req.url] = raw

def base_thread(client: Client,
                segments: Generator,
                callback: Callable,
                delay: float = .05) -> dict[str, bytes]:
    '''
    Base downloader for threaded backends.
    
    Inspired by: https://github.com/Egsagon/neko-sama-api/blob/ad34184823072f98abbee1a90b111358a6b39cb2/src/nekosama/download.py#L112
    '''
    
    # Prepare requests
    reqs = [
        client.session.prepare_request(
            requests.Request(
                'GET', segment, consts.HEADERS | client.language
            )
        )
        for segment in segments
    ]
    
    buffer = {}
    length = len(list(reqs))
    queue = copy.deepcopy(reqs)
    
    while len(queue):
        current = queue.pop(0)

        thread = threading.Thread(
            target = _thread,
            kwargs = dict(req = current, session = client.session,
                         buffer = buffer, queue = queue, delay = delay)
        )
        
        thread.start()
        time.sleep(delay) # Decay thread starting
        callback(len(buffer), length)
    
    print('chunk end')
    
    # Check for missing chunks
    for i, req in enumerate(reqs):
        if not req.url in buffer.keys():
            
            print('Downloading missing', i)
            buffer[req.url] = _thread(req, client.session, delay, client.session)
            callback(i, length)
    
    callback(length, length)
    return buffer

def threaded(video: Video,
             quality: Quality,
             callback: Callable,
             path: str,
             delay: float = .05) -> bytes:
    '''
    Threaded download.
    '''
    
    segments = video.get_segments(quality)
    buffer = base_thread(video.client, segments, callback, delay)
    items = sorted(buffer.items(), key = lambda row: row[0])
    
    raw = b''
    
    for url, value in items:
        print(f'{url = }')
        raw += value
    
    # Write to file
    with open(path, 'wb') as file:
        file.write(raw)

# EOF