Video downloading
=================

Downloading a video
-------------------

A video can be downloaded via its :meth:`.Video.download`
method.

.. code-block:: python

    import phub
    from phub.locals import Quality

    video = ...

    video.download(path = 'my-video.mp4',
                   quality = Quality.BEST)

Download options
----------------

^^^^^^^^^^^
Output path
^^^^^^^^^^^

The video output path can be either a path to a file, in which
case the given file will be erased, or a directory. If that is
the case, the final path of the file can be found by capturing the output of
the :meth:`.Video.download` method.

.. code-block:: python

    video.download('video.mp4')  # video.mp4 
    video.download('dir/')       # dir/<video-key>.mp4

^^^^^^^^^^^^^
Video quality
^^^^^^^^^^^^^

There are multiple ways you can create a quality object.

.. code-block:: python

    from phub import Quality

    quality = Quality.BEST             # Using a constant
    quality = Quality('best')          # Using a string
    quality = Quality(1080)            # Using an int
    quality = Quality(Quality('best')) # Using an object
    
    # Alternatively, you can also enter a raw quality inside most PHUB methods:
    video.download(quality = Quality.BEST)
    # is the same as
    video.download(quality = 'best')

^^^^^^^^^^^^^^^^^^^^^^^
Simple progress display
^^^^^^^^^^^^^^^^^^^^^^^

The progress of the download can be displayed using built-in functions, from the
`.display` submodule. There are several presets available:

.. code-block:: python

    >>> import phub
    >>> import phub.display as display
    >>> video = phub.Client().get('xxx')

    # Simple colored progress (default)
    >>> video.download(..., display = display.progress(color = True))
    Downloading 50% [150/300]

    # Bar progress
    >>> video.download(..., display = bar())
    Downloading |========        | [150/300]

    # STD file progress
    >>> video.download(..., display = std(file = sys.stdout))
    50

You can also define your own progress callback.
Your callback shall take 2 arguments: the currently processing segment,
and the total segment to process.

.. code-block:: python

    def show_progress(current_segment: int, total_segment: int):
        # E.g. Display percentage progress

        percentage = round( (current_segment / total_segment) * 100 )

        print(f'Downloading: {percentage}%')

    video.download(..., display = show_progress)


^^^^^^^^^^^
FFmpeg converting
^^^^^^^^^^^

Videos are downloaded using HLS streaming. Basically we use smaller segments and put them into one file. This file
can usually be played by any video player except for a few exceptions. However, you won't be able to add metadata to it.
Although it has a .mp4 extension it actually is a .ts file. If you want to convert a video to a valid mp4 file and assign
the needed headers to it, you can use FFmpeg for that.

When downloading a video, use `convert = True` as an argument in there.
For example:

..  code-block:: python
    import phub
    video = phub.Client().get_video("some_url")
    video.download(quality="best", path="./", convert=True) # This converts the video


You can define the location for ffmpeg using:

.. code-block:: python
    import consts
    consts.FFMPEG_EXECUTABLE = "<your_path_to_ffmpeg>

By default, phub will search for it in your system's path

^^^^^^^^^^^
Downloaders
^^^^^^^^^^^

You can specify custom downloaders to download your video.
There are a few presets available in the `.download` submodule.

.. code-block:: python

    import phub
    import phub.download as download

    client = phub.Client()
    video = client.get('xxx')

    # Dummy download - Slow, but stable
    video.download(..., downloader = download.default)

    # FFMPEG download - Everything is handled by FFMPEG
    # Note - you need to have FFMPEG installed to your system.
    video.download(..., downloader = download.FFMPEG)

    # Threaded download - Uses python futures to download
    # the video as fast as possible. Multiple settings are available
    # for you to set an appropriate download speed depending on your
    # computer and internet connection. 
    video.download(..., downloader = download.threaded(max_workers = 50,
                                                       timeout = 10))

You can also specify custom downloaders.
You can use :meth:`.Video.get_segments`, which outputs a generator
containing a list of segment URLs.

.. code-block:: python

    import phub

    def my_downloader(video, quality, callback, path):
        # Over simplified downloader

        # Get segment list
        segments = list(video.get_segments(quality))
        length = len(segments)

        # Open file
        with open(path, 'wb') as file:
            for i, url in enumerate(segments):

                # Download one segment and write it
                raw = video.client.call(url)
                file.write(raw)

                # Update the callback
                callback(i, length)
    
    video.download(..., downloader = my_downloader)

Alternatively, :meth:`.Video.get_M3U_url` outputs the URL of the master
M3U file for a desired quality.

For instance, the following downloader will download the M3U8 file of a video:

.. code-block:: python

    import os
    import phub

    client = phub.Client()
    video = client.get('...')

    def m3u_downloader(video, quality, callback, path):

        url = video.get_M3U_url(quality = quality)

        with open(path, 'wb') as file:

            raw = video.client.call(url)
            file.write(raw.content)
        
    video.download('master.m3u8', quality = 'best', downloader = m3u_downloader)
