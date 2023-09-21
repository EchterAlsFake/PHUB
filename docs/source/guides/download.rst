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
the case, 

The final path of the file can be found by capturing the output of
the :meth:`.Video.download` method. 

^^^^^^^^^^^^^
Video quality
^^^^^^^^^^^^^

The quality of the video can be designed as:

* A constant from `phub.Quality`, e.g. `phub.Quality.BEST`.
* An absolute value (`int`): 1080, 720, etc.
* A string representing `phub.Quality` constants, like `best`, `half`, `worst`.

^^^^^^^^^^^^^^^^
Progress display
^^^^^^^^^^^^^^^^

The progress of the video can be displayed using built-in functions, from the
`phub.display` submodule.

* Simple progress (default)
    Displays a colored output progress.

    .. code-block:: python

        >>> from phub.display import progress

        >>> video.download(..., display = progress(color = True))
        Downloading 50% [150/300]

* Bar progress
    Displays a tqd-like progress bar.

    .. code-block:: python

        >>> from phub.display import bar
        
        >>> video.download(..., display = bar())
        Downloading |========        | [150/300]

* STD progress
    Really Simple display to be grepped or something.

    .. code-block:: python

        >>> import sys
        >>> from phub.display import std
        
        >>> video.download(..., display = std(file = sys.stdout))

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
Downloaders
^^^^^^^^^^^

.. warning:: Unstable feature

You can specify custom downloaders to download your video.
There are a few presets available in the `phub.download` submodule.

* Dummy download (default)
    A slow, dummy downloader that fetch each segment after the another,
    concatenate them on the fly and write them to the file at the end.

    .. code-block:: python

        from phub.download import default
        video.download(..., downloader = default)

* FFMPEG download
    This preset will use FFMPEG to download the file.
    FFMPEG atomatically set the apropriate download speeds
    between segments download and codecs stuff, which makes it
    much faster and reliable than some presets.

    .. code-block:: python

        from phub.download import FFMPEG
        video.download(..., downloader = FFMPEG)

* Threaded download
    .. warning:: Unstable: Currently in development.

    This preset will use threads to download segments as fast as
    it can, and writing them after.

    .. code-block:: python

        from phub.download import threaded
        video.download(..., downloader = threaded)


You can also specify custom downloaders.

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

Even more advanced downloading
------------------------------

If :meth:`.Video.download` is not advanced enough for you,
here are a few other more bare-bone methods. 

You can use :meth:`.Video.get_segments`, which outputs a
generator containing a list segment URLs. See the
``my_downloader`` exemple above.

If you want something even more bare-bone, use
:meth:`.Video.get_M3U_url`. This outputs the URL of the master
M3U file for a desired quality. This can be used, for exemple,
with FFMPEG (if you want to have more control over it than with
``phub.download.FFMPEG``).

.. code-block:: python

    import os
    import phub
    from phub.locals import Quality

    video = ...

    # Get the M3U url
    M3U = video.get_M3U_url(quality = Quality.BEST)

    # Use PHUB default FFMPEG command:
    # ffmpeg -i "{input}" -bsf:a aac_adtstoasc -y -c copy {output}
    cmd = phub.consts.FFMPEG_COMMAND.format(
        input = M3U,
        output = 'my-video.mp4'
    )

    # Execute the command
    os.system(cmd)
