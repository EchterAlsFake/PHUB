Video downloading
=================

Downloading a video
-------------------

A video can be downloaded via its :meth:`.Video.download`
method.

.. code-block:: python

    import phub
    from phub import Quality

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

* A constant from `phub.Quality`, e.g. `phub.Quality.BEST`;
* An absolute value (`int`): 1080, 720, etc.
* A string representing `phub.Quality` constants, like `best`, `half`, `worst`.

^^^^^^^^^^^^^^^^^
Progress callback
^^^^^^^^^^^^^^^^^

A function used to be called to communicate the progress of the
downloads. Ideally, the function takes two arguments of type `int`:
The current segment being processed, and the total of segments.

.. code-block:: python

    def callback(current: int, total: int) -> None:

        print('Downloading:', current, '/', total)

    video.download(path = '.',
                    quality = 'best',
                    callback = callback)

This code block will print a new line each time progress is made.

Presets
"""""""

PHUB comes with some presets for easy progress display.
Theses presets can be found by importing download_presets.

.. code-block:: python
    
    from phub.utils import download_presets as dlp 

.. note::

    Theses presets use wrappers, so you have to actually *call* the
    preset function inside :meth:`.Video.download`.
    This is because most of those presets don't have contexts.  

* `dlp.bar`

    The default preset. It uses a `tqdm`_ bar to display progress.
    You can pass arguments to this function, they will be passed to
    the tqdm bar initiator, e.g.:

    .. code-block:: python

        video.download(..., callback = dlp.bar(desc = 'Downloading'))
    
    .. code-block:: bash

        Downloading 100%|███████████████████████████████▉| 8014/8014 [...]

    You can find out more parameters in the `tqdm docs`_.

.. _tqdm docs: https://tqdm.github.io/docs/tqdm/#tqdm-objects

* `dlp.progress`

    Simple download progress that calculates a percentage.
    You can control wether to use ANSI color codes to decorate
    the progress.

    .. code-block:: python

        video.download(..., callback = dlp.progress(color = True))

    .. code-block:: bash

        Downloading: 100% [8014/8014]

* `dlp.std`

    This is the simplest default callback; In fact, it is so simple
    that you might forget that it exists and write your own callback
    for it.

    It is meant to be used by other softwares, in the style of a bash
    script or a EWW widget. It simply adds a new line to the console
    each time there is a progress in the download and dispays the
    percentage.
    You can control in which file the progress must be displayed.

    .. code-block:: python

        import sys

        video.download(..., callback = dlp.std(file = sys.stdout))


^^^^^^^^^^^^^^^
Maximum retries
^^^^^^^^^^^^^^^

If you have a low connection and you know some parts of the video
might fail to download, you can insist by setting this value higher.

More precisely, `max_retries` determines how many times the downloader
should try to download the same segment before moving on to the next
one.

.. code-block:: python

    video.download(..., max_retries = 10)

Advanced downloading
--------------------

The :meth:`.Video.download` method is really simple: It
requests each video segment one at a time and concatenate it
on the fly to a video file. While this is ok for downloading
one or more video, you might want extra speed in certain
scenarios.

In that case, you can fetch the M3U file
:meth:`.Video.get_M3U`. It takes a ``process`` argument, wether
to process the file.

.. note:: A M3U file is (basically) just a list of URLs to call to reconstituate the video. It also has comments on stuff like bandwith, resolution, timing, etc.

* If ``True``, The M3U file will be parsed and returned as a python list of URLs.
* Else, the M3U file will be given as is, except with adjusted URL pathes.

Here is an exemple to process that file and handling it to
FFMPEG, which is able to download videos from M3U files.

.. code-block:: python

    import os
    import phub
    
    client = phub.Client()
    video = client.get(key = 'xxx')

    # Write to a temp file
    with open('file.m3u8', 'w') as file:

        file.write( video.get_M3U(quality = Quality.BEST,
                                  process = False) )
    
    # Then we can call FFMPEG (i think this should work)
    # ffmpeg -i file.m3u8 my-video.mp4

You can also use ay kind of threaded downloaders.

.. _tqdm: https://pypi.org/project/tqdm/