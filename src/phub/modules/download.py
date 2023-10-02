from __future__ import annotations

import time
import logging

import os
from typing import TYPE_CHECKING, Callable
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed

from .. import consts
from ..objects import Callback

if TYPE_CHECKING:
    from .. import Client
    from ..objects import Video
    from ..locals import Quality


logger = logging.getLogger(__name__)

CallbackType = Callable[[int, int], None] | Callback


def default(video: Video,
            quality: Quality,
            callback: CallbackType,
            path: str,
            start: int = 0) -> None:
    '''
    Dummy downloader. Fetch a segment after the other.
    
    Args:
        video       (Video): The video object to download.
        quality   (Quality): The video quality.
        callback (Callable): Download progress callback.
        path          (str): The video download path.
        start         (int): Where to start the download from. Used for download retries.
    '''
    
    logger.info('Downloading using default downloader')
    
    buffer = b''
    
    segments = list(video.get_segments(quality))[start:]
    length = len(segments)
    
    callback = Callback.new(callback, length)
    
    # Fetch segments
    for i, url in enumerate(segments):
        for _ in range(consts.DOWNLOAD_SEGMENT_MAX_ATTEMPS):
        
            try:
                segment = video.client.call(url, throw = False, timeout = 4)
                
                if segment.ok:
                    buffer += segment.content
                    callback.on_write(i + 1)
                    break
                
            except Exception as err:
                logger.error('Error while downloading: %s', err)
            
            logger.warning('Segment %s failed. Retrying.', i)
            time.sleep(consts.DOWNLOAD_SEGMENT_ERROR_DELAY)
                
        else:
            logger.error('Maximum attempts reached. Refreshing M3U...')
            return default(video, quality, callback, i - 1)
        
        callback.on_download(i + 1, length)
    
    # Concatenate
    logger.info('Concatenating buffer to %s', path)
    with open(path, 'wb') as file:
        file.write(buffer)
        
    logger.info('Downloading successfull.')

def FFMPEG(video: Video,
           quality: Quality,
           callback: CallbackType,
           path: str) -> None:
    '''
    Download using FFMPEG. It has to be installed to your system.
    You can override FFMPEG access with consts.FFMPEG_COMMAND
    
    Args:
        video       (Video): The video object to download.
        quality   (Quality): The video quality.
        callback (Callable): Download progress callback (Unused).
        path          (str): The video download path.
        start         (int): Where to start the download from. Used for download retries.
    '''
    
    logger.info('Downloading using FFMPEG')
    M3U = video.get_M3U_URL(quality)
    
    callback = Callback.new(callback, 1)
    command = consts.FFMPEG_COMMAND.format(input = M3U, output = path)
    logger.info('Executing `%s`', command)
    
    # Execute
    callback = Callback.on_download(callback, 0)
    callback = Callback.on_write(callback, 0)
    os.system(command)
    callback = Callback.on_write(callback, 1)
    callback = Callback.on_download(callback, 1)

def _thread(client: Client, url: str, timeout: int) -> bytes:
    '''
    Download a single segment.
    '''
    
    return client.call(url, timeout = timeout).content

def _base_threaded(client: Client,
                   segments: list[str],
                   callback: CallbackType,
                   max_workers: int = 50,
                   timeout: int = 10) -> dict[str, bytes]:
    '''
    base thread downloader for threaded backends.
    '''
    
    logger.info('Threaded download amorced')
    
    with Pool(max_workers = max_workers) as executor:
        
        buffer: dict[str, bytes] = {}
        
        while 1:
            
            futures = {executor.submit(_thread, client, url, timeout): url
                       for url in segments}
            logger.info('%s futures submited', len(futures))
            
            for future in as_completed(futures):
                
                url = futures[future]
                
                try:
                    segment = future.result()
                    buffer[url] = segment
                    
                    # Remove future and call callback
                    futures.pop(future)
                    callback.on_download(len(buffer))
                
                except Exception as err:
                    logger.warn('Segment %s failed: %s', url, err)
                    future.cancel()
            
            if lns := len(futures):
                logger.warn('%s segments failed to download, retrying...', lns)
                
                print('\n', futures)
                
                continue
            
            break
    
    logger.info('Threaded download finished')
    
    return buffer

def threaded(max_workers: int = 100,
             timeout: int = 30) -> Callable:
    '''
    Simple threaded downloader.
    
    Args:
        max_workers (int): How many downloads can take place simoultaneously.
        timeout (int): Maximum time before considering a download failed.
    
    Returns:
        Callable: A download wrapper.
    '''
    
    def wrapper(video: Video,
                quality: Quality,
                callback: CallbackType,
                path: str) -> None:
        '''
        Wrapper.
        '''
        
        segments = list(video.get_segments(quality))
        total = len(segments)
        callback = Callback.new(callback, total)
        
        buffer = _base_threaded(
            client = video.client,
            segments = segments,
            callback = callback,
            max_workers = max_workers,
            timeout = timeout)
        
        # Concatenate and write
        with open(path, 'wb') as file:
            for i, url in enumerate(segments):
                file.write(buffer.get(url, b''))
                callback.on_write(i)
    
    return wrapper

def threaded_FFMPEG(max_workers: int = 10,
                    timeout: int = 5) -> Callable:
    '''
    Wrapper.
    '''
    
    def wrapper(video: Video,
                quality: Quality,
                callback: CallbackType,
                path: str) -> None:
        '''
        Wrapper.
        '''
        
        raise NotImplementedError()
        
        segments = list(video.get_segments(quality))
        total = len(segments)
        callback = Callback.new(callback, total)
        
        buffer = _base_threaded(
            client = video.client,
            segments = segments,
            callback = callback,
            max_workers = max_workers,
            timeout = timeout)
        
        # TODO

    return wrapper

# EOF