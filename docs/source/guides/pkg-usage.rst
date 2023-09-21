Package Usage
=============

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
    video = client.get(url) # (1)!
    # video will be a phub.Video object

.. code-annotations::
    #.
        Note that you can also load the video 
        using the `viewkey` paramater in the URL.

        .. code-block:: python

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

* The ``path`` of the video can be a file or a directory, in which case the title of the video will be taken as a filename.

For advanced downloading, see downloading.

Debugging
---------

At any time, you can use built-in debugging to see what's wrong with
your code or the API.

.. code-block:: python

    import phub

    # Start debug
    phub.debug(True)

    client = phub.Client()
    ...
