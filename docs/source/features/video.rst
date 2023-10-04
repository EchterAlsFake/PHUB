Using Videos
============

:py:class:`.Video` objects are emitted by:

- :meth:`.Client.get` when searching for a specific video
- :meth:`.Query.get` when enumerating for videos in a query

Once initialised, a :py:class:`.Video` object does not do anything.
It manages requests and caching automatically to be as fast as possible.

You can use the following properties on a video:

.. default-literal-role:: python

* :literal:`video.title`

    The original video title. It might
    depend on the :doc:`client language </api/objects>`.

* :literal:`video.image`

    The video thumbnail, as an :py:class:`.Image` object.

    You can download the image or access its URL for embedding:
    
    :literal:`video.image.url`
    :literal:`video.image.download('.')`

* :literal:`video.is_vertical`

    Wether the video is in vertical (phone) mode, as a
    :py:class:`bool`.

* :literal:`video.orientation`

    The sexual orientation of the video (straight, gay, etc.).
    Also called :literal:`segment`.

* :literal:`video.duration`

    The length of the video, as a :py:class:`datetime.timedelta`
    object.

    You can access its total seconds, or do other stuff:
    :literal:`video.duration.total_seconds()`

* :literal:`video.tags`

    The tags of the video. Each tag is represented as a
    :py:class:`.Tag` object.

* :literal:`video.like`

    Both upvotes and downvotes are represented with the
    :py:class:`.Like` object.

    .. code-block:: python
        
        video.like.up       # Upvotes
        video.like.down     # Downvotes
        video.like.ratings  # coefficient

* :literal:`video.views`

    The video views, as an :py:class:`int`.

* :literal:`video.hotspots`

    The video hotspots. This is used by Pornhub to display
    the bar above the player progress bar, and probably the
    video preview. It is represented as a :py:class:`int`
    generator.

* :literal:`video.date`

    The video release date, as a :py:class:`datetime.datetime`
    object.

* :literal:`video.pornstars`

    The pornstars in the video, represented as a list of
    :py:class:`.User` objects.

* :literal:`video.categories`

    The categories the video is referenced in. Represented as a
    :py:class:`.Category` generator.

    .. default-literal-role::

    .. warning::
        All categories link to ``phub.locals.Category`` constants.
        If the constant does not exist, a temporary one is created,
        but it is recommended that you update PHUB's constants:
        :literal:`python -m phub update_locals`
    
    .. default-literal-role:: python
    
    You can compare categories together and use them back as
    search filter, e.g.:

    .. code-block:: python

        for category in video.categories:

            print(category)
            query = client.search(filter = category)

* :literal:`video.author`

    The user account that posted the video, as a :py:class:`.User`
    object.

    E.g.:

    .. code-block:: python

        video = ...

        print(f'The author of this video is {video.author.name}!')

Refreshing data
---------------

For long-term usage, you might want to refresh all
this data, which is cached by all :py:class:`.Video`
objects.

You can simply do:

.. code-block:: python

    video.refresh(page = True, data = True)

You can also choose to refresh the video page
(used for web-scraping), or the data page
(fetched from the HubTraffic API), or both.

For exemple:

.. code-block:: python

    # Watch a video like counter

    import time
    import phub

    client = phub.Client()
    video = client.get(...)

    while 1:
        print(f'The video has {video.like.up} likes!')

        time.sleep(60 * 10) # Every 10 min
        video.refresh()
