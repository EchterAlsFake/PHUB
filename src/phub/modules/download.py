from __future__ import annotations

import os
import time
import logging
from typing import TYPE_CHECKING, Callable
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed
from ffmpeg_progress_yield import FfmpegProgress

import requests.adapters

from .. import consts

if TYPE_CHECKING:
    from .. import Client
    from ..objects import Video
    from ..locals import Quality

logger = logging.getLogger(__name__)

CallbackType = Callable[[int, int], None]


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
    
    # Fetch segments
    for i, url in enumerate(segments):
        for _ in range(consts.DOWNLOAD_SEGMENT_MAX_ATTEMPS):
        
            try:
                segment = video.client.call(url, throw = False, timeout = 4, silent = True)
                
                if segment.ok:
                    buffer += segment.content
                    callback(i + 1, length)
                    break
            
            except Exception as err:
                logger.error('Error while downloading: %s', err)
            
            logger.warning('Segment %s failed. Retrying.', i)
            time.sleep(consts.DOWNLOAD_SEGMENT_ERROR_DELAY)
                
        else:
            logger.error('Maximum attempts reached. Refreshing M3U...')
            return default(video, quality, callback, i - 1)
    
    # Concatenate
    logger.info('Concatenating buffer to %s', path)
    with open(path, 'wb') as file:
        file.write(buffer)
    
    logger.info('Downloading successful.')

def FFMPEG(video: Video, quality: Quality, callback: CallbackType, path: str, start: int = 0) -> None:
    '''
    Download using FFMPEG with real-time progress reporting.
    FFMPEG must be installed on your system.
    You can override FFMPEG access with consts.FFMPEG_COMMAND.

    Args:
        video       (Video): The video object to download.
        quality   (Quality): The video quality.
        callback (Callable): Download progress callback.
        path          (str): The video download path.
        start         (int): Where to start the download from. Used for download retries.
    '''

    logger.info('Downloading using FFMPEG')
    M3U = video.get_M3U_URL(quality)

    # If FFMPEG_COMMAND is a string needing format, replace it with direct list construction
    command = [
        f"{consts.FFMPEG_EXECUTABLE}",
        "-i", M3U,
        "-bsf:a", "aac_adtstoasc",
        "-y",
        "-c", "copy",
        path  # Output file path
    ]

    # Log the command being executed
    logger.info('Executing `%s`', ' '.join(command))

    # Initialize FfmpegProgress and execute the command
    try:
        ff = FfmpegProgress(command)
        for progress in ff.run_command_with_progress():
            # Update the callback with the current progress
            callback(round(progress), 100)

            if progress == 100:
                logger.info("Download successful")

    except Exception as err:
        logger.error('Error while downloading: %s', err)


def _thread(client: Client, url: str, timeout: int) -> bytes:
    '''
    Download a single segment.
    '''
    
    return client.call(url, timeout = timeout, silent = True).content


def _base_threaded(client: Client,
                   segments: list[str],
                   callback: CallbackType,
                   max_workers: int = 50,
                   timeout: int = 10,
                   disable_client_delay: bool = True) -> dict[str, bytes]:
    '''
    base thread downloader for threaded backends.
    '''
    
    logger.info('Threaded download amorced')
    length = len(segments)
    
    # Mount special adapter for handling large requests
    logger.info('Mounting download adapter')
    old_adapter = client.session.adapters.get('https://')
    adapter = requests.adapters.HTTPAdapter(pool_maxsize = max_workers)
    client.session.mount('https://', adapter)

    with Pool(max_workers = max_workers) as executor:
        logger.info('Opened executor')
        
        buffer: dict[str, bytes] = {}
        segments = segments.copy() # Avoid deleting parsed segments
        
        while 1:
            futures = {executor.submit(_thread, client, url, timeout): url
                       for url in segments}
            
            logger.info('Submitted %s futures, starting executor', len(futures))
            
            for future in as_completed(futures):
                
                url = futures[future]
                segment_name = consts.re.ffmpeg_line(url)
                
                # Disable delay
                client.start_delay = not disable_client_delay
                
                try:
                    segment = future.result()
                    buffer[url] = segment
                    
                    # Remove future and call callback
                    segments.remove(url)
                    callback(len(buffer), length)
                
                except Exception as err:
                    logger.warning('Segment `%s` failed: %s', segment_name, err)
            
            if lns := len(segments):
                logger.warning('Retrying to fetch %s segments', lns)
                continue
            
            break
    
    logger.info('Threaded download finished, mounting back old adapter')
    client.session.mount('https://', old_adapter)
    
    return buffer

def threaded(max_workers: int = 100,
             timeout: int = 30) -> Callable:
    '''
    Simple threaded downloader.
    
    Args:
        max_workers (int): How many downloads can take place simultaneously.
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
        
        buffer = _base_threaded(
            client = video.client,
            segments = segments,
            callback = callback,
            max_workers = max_workers,
            timeout = timeout
        )
        
        # Concatenate and write
        logger.info('Writing buffer to file')
        with open(path, 'wb') as file:
            for url in segments:
                file.write(buffer.get(url, b''))
        
        logger.info('Successfully wrote file to %s', path)
    
    return wrapper

# EOF