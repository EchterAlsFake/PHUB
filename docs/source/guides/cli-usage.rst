CLI Usage
=========

PHUB comes with a built-in CLI for downloading videos.

It uses the `click`_ dependency.

.. _click: https://pypi.org/project/click/

.. code-block:: bash

    $ python -m phub

.. code-block:: bash

    Usage: python -m phub [OPTIONS] INPUT

    Options:
    --output TEXT      Output file or directory
    --quality TEXT     Video quality
    --downloader TEXT  Video downloader (default, FFMPEG or threaded)
    --help             Show this message and exit.

Input
    can be a video URL or a file containing multiple URLs.
    quality

Output
    Output video file or directory. If you are downloading multiple
    videos at once, make sure it's a directory.

Quality
    The desired video quality. Usually 'best', 'half' or 'worst'.
    If an integer is specified, the nearest quality to that number
    will be picked.

Downloader
    The backend used to download the video. Possible values:
    - default: download segments one by one. Safe but slow.
    - FFMPEG: Use FFMPEG to download faster.
    - threaded: Even faster downloader using threads. 
