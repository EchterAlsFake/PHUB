from __future__ import annotations

import time
import logging
import requests.adapters
from pathlib import Path
from typing import TYPE_CHECKING, Callable
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed
from ffmpeg_progress_yield import FfmpegProgress
from .. import consts

if TYPE_CHECKING:
    from .. import Client
    from ..objects import Video
    from ..utils import Quality

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

def FFMPEG(video: Video, quality: Quality, callback: CallbackType, path: str | Path, start: int = 0) -> None:
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
        str(path)  # Output file path
    ]

    # Log the command being executed
    logger.info('Executing `%s`', ' '.join(map(str, command)))

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
    Download a single segment using the client's call method.
    This function is intended to be used within a ThreadPoolExecutor.
    '''
    try:
        response = client.call(url, timeout=timeout, silent=True)
        response.raise_for_status()  # Assuming client.call returns an object with a similar interface to requests.Response
        return (url, response.content, True)

    except Exception as e:
        logging.warning(f"Failed to download segment {url}: {e}")
        return (url, b'', False)


# Modify _base_threaded to use ThreadPoolExecutor
def _base_threaded(client: Client, segments: list[str], callback: CallbackType, max_workers: int = 20,
                   timeout: int = 10) -> dict[str, bytes]:
    '''
    Base threaded downloader using ThreadPoolExecutor.
    '''
    logging.info('Threaded download initiated')
    buffer = {}
    length = len(segments)
    logger.info('Mounting download adapter')
    old_adapter = client.session.adapters.get('https://')
    adapter = requests.adapters.HTTPAdapter(pool_maxsize = max_workers)
    client.session.mount('https://', adapter)

    with Pool(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(_thread, client, url, timeout): url for url in segments}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, data, success = future.result()
                if success:
                    buffer[url] = data
                # Regardless of success, update the progress
                callback(len(buffer), length)
            except Exception as e:
                logging.warning(f"Error processing segment {url}: {e}")

    client.session.mount('https://', old_adapter)
    return buffer


def threaded(max_workers: int = 20,
             timeout: int = 10) -> Callable:
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