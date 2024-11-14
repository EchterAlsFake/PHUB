CLI Usage
=========

PHUB comes with a built-in CLI for downloading videos.

.. code-block:: bash

    $ phub

.. code-block:: bash

    Usage: phub [OPTIONS]

    Options:
    -output      TEXT    Output file or directory
    -quality     TEXT    Video quality
    -downloader  TEXT    Video downloader (default, ffmpeg or threaded)
    -url         TEXT    Video URL
    -model       TEXT    Model URL
    -file        TEXT    Path to a file containing URLs of Video (separated with new lines)
    -video_limit Number  Limits how many videos of a model will be downloaded (default: all)
    --help               Show this message and exit.

Quality
    The desired video quality. Choose between 'best', 'half' or 'worst'.

Downloader
    The backend used to download the video. Possible values:
    - default: download segments one by one. Safe but slow.
    - FFMPEG: Use FFMPEG to download faster.
    - threaded: Even faster downloader using threads. 
