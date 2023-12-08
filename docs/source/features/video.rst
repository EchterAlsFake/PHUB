Using Videos
============

:py:class:`.Video` objects are emitted by:

- :meth:`.Client.get` when searching for a specific video
- :meth:`.Query.get` when enumerating for videos in a query

Once initialised, a :py:class:`.Video` object does not do anything.
It manages requests and caches automatically to be as fast as possible.

You can use the following properties on a video:

.. default-literal-role:: python

.. list-table:: PHUB Video Properties
    :header-rows: 1

    * - Property
      - Description
    
    * - :literal:`video.title`
      - Video title. Might depend on client language.
    
    * - :literal:`video.image`
      - Video thumbnail, as a :py:class:`.Image` object.

    * - :literal:`video.is_vertical`
      - Whether the video is in vertical (phone) mode, as a :py:class:`bool`.

    * - :literal:`video.orientation`
      - The sexual orientation of the video (straight, gay, etc.).
    
    * - :literal:`video.duration`
      - The length of the video, as a :py:class:`datetime.timedelta` object.

    * - :literal:`video.tags`
      - List of video tags. Each tag is represented as a :py:class:`.Tag` object.

    * - :literal:`video.like`
      - Votes representation as a :py:class:`.Like`object.

    * - :literal:`video.views`
      - The video views (:py:class:`int`).

    * - :literal:`video.hotspots`
      - Video hotspots. Used by Pornhub player to display hot moments. Represented as an :py:class:`int` generator.

    * - :literal:`video.date`
      - The video release date, as a :py:class:`datetime.datetime` object.

    * - :literal:`video.pornstars`
      - Pornstars in the video, represented as a list of :py:class:`.User` objects.

    * - :literal:`video.categories`
      - The video categories. Represented as a :py:class:`.Category` generator.
    
    * - :literal:`video.author`
      - The user account that posted the video, as a :py:class:`.User` object.

Refreshing data
---------------

Refreshing `.Video` objects is done through the :meth:`.Video.refresh` method.

.. code-block:: python

    # Watch the video counter

    import time
    import phub

    client = phub.Client()
    video = client.get(...)

    while 1:
        print(f'The video has {video.like.up} likes!')

        time.sleep(60 * 10) # Every 10 min
        video.refresh()
