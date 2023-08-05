Quickstart
==========

Installation
------------

You can install PHUB from the command line
using pip:

``pip install -U phub``

Or, if you want to get the latest features,
you can install using the project master
branch:

``pip install -U git+https://github.com/Egsagon/PHUB.git``

Initialising a session
----------------------

First thing to do is setting up a client.
A client represents one connection to PH,
but you can use multiple at the same time.
You can also specify a custom language
locale (``en`` by default). This will
affect searching preferences, video titles,
etc.

.. code-block:: python

    import phub

    client = phub.Client(language = 'en')

Fetching a video
----------------

If you want to work with a specific video
you know the URL of, you can initialise it
like so:

.. code-block:: python

    import phub

    client = phub.Client()

    url = 'https://www.pornhub.com/view_video.php?viewkey=xxx'
    video = client.get(url)
    # video will be a phub.Video object

    # Note - You can also load the video 
    # using its `viewkey` https argument
    # if you think that improves clarity.
    video = client.get(key = 'xxx')

Accessing video data
--------------------

By default, video data will be pre-scrapped
when you call :meth:`.Client.get`.
You can turn that off by specifying
``preload`` to ``False``.


.. code-block:: python

    >>> import phub
    >>> client = phub.Client()
    >>> video = client.get(key = 'xxx')

    >>> video.title
    'Minecraft speedrunner vs 5 hunter'

    >>> video.like.up
    4500000000

    >>> video.author
    phub.Author(name = 'Dream')

At any time you can reload that data by calling
:meth:`.Client.refresh` (useful for long-term usage).

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

* The ``path`` of the video can be a file or a directory, in
which case the title of the video will be taken as a filename.

Advanced downloading
--------------------

The :meth:`.Video.download` method is really simple: It
requests each video segment one at a time and concatenate it
on the fly to a video file. While this is ok for downloading
one or more video, you might want extra speed in certain
scenarios.

In that case, you can fetch the M3U file
:meth:`.Video.get_M3U`. It takes a single argument, wether
to process the file.

.. note:: A M3U file is (basically) just a list of URLs to call
    to reconstituate the video. It also has comments on stuff
    like bandwith, resolution, timing, etc.

* If ``True``, The M3U file will be parsed and returned as a python list of URLs.
* Else, the M3U file URL will be given.

.. note:: If you choose to work with the raw M3U file, keep
    in mind that the given URLs are relatives, you will have
    to get and add the CDN root to each of them.

Here is an exemple to process that file and handling it to
FFMPEG, which is able to download videos from M3U files.

.. code-block:: python

    import os
    import phub
    from phub import Quality

    client = phub.Client()
    video = client.get(key = 'xxx')

    url = video.get_M3U(quality = Quality.BEST,
                        process = False)

    # Get CDN dir
    root = url.split('master.m3u8')[0]

    # Get the content of the M3U file
    M3U = client._call('GET', url, simple_url = False)

    # Write to a temp file
    with open('file.m3u8', 'w') as file:

        # For each line, if the line isn't a comment,
        # We write the URL root before writing the line. 
        for line in M3U.content.split('\n'):
            if not line.startswith('#'):
                file.write(root)
        
        file.write(line + '\n')
    
    # Then we can call FFMPEG
    os.popen('ffmpeg -i file.m3u8 my-video.mp4')

.. note:: Ik this is more complicated than it should, i'll
    try to simplify it in the future.