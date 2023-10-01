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

.. code-annotations::
    #.
        Note that you can also load the video 
        using the `viewkey` paramater in the URL.

        .. code-block:: python

            video = client.get(key = 'xxx')

Accessing data
--------------

With a :py:class:`.Video` object: you can fetch all video data, e.g.:

.. code-block:: python

    >>> video: phub.Video = ...

    >>> video.title
    >>> video.duration
    >>> video.like.up
    >>> video.like.down
    >>> video.views
    >>> video.tags
    >>> video.pornstars
    >>> video.author
    >>> video.date
    >>> video.image
    # etc.

You can check out all video properties `here </api/objects#phub.objects.Video>`.

Downloading a video
-------------------

A video can be downloaded via :meth:`.Video.download`.

.. code-block:: python

    import phub
    from phub.locals import Quality

    video = ...

    video.download(path = 'my-video.mp4',
                   quality = Quality.BEST)

You can set the quality to be ``BEST``, ``HALF`` or ``WORST``, or an :py:class:`int`
for an absolute value.

.. note:: Tip: you can set the ``path`` paramater to be a directory for the video
    to be downloaded in. The file name will automatically be the video id. 

For advanced downloading, see `/guides/download`.

Debugging
---------

You can use Python `logging`_ library to debug your code and see what's wrong with
it or the API.

.. _logging: https://docs.python.org/3/library/logging.html

.. code-block:: python

    import phub
    import logging

    logging.BasicConfig(level = ...)

    client = phub.Client()
    ...

