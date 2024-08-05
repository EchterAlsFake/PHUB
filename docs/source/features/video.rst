Using Videos
============

:py:class:`.Video` objects are emitted by:

- :meth:`.Client.get` when searching for a specific video
- :py:class:`.Query` when enumerating for videos in a query

Once initialised, a :py:class:`.Video` object does not do anything.
It manages requests and caches automatically to be as fast as possible.

You can use the following properties on a video:

.. default-literal-role:: python

.. list-table:: PHUB Video Properties
    :header-rows: 1

    * - Property
      - Type
      - Description
    
    * - :literal:`video.title`
      - :py:class:`str`
      - Video title. Might depend on client language.
    
    * - :literal:`video.image`
      - :py:class:`.Image`
      - The video thumbnail.

    * - :literal:`video.is_vertical`
      - :py:class:`bool`
      - Whether the video is in vertical (phone) mode.

    * - :literal:`video.orientation`
      - :py:class:`str`
      - The sexual orientation of the video (straight, gay, etc.).
    
    * - :literal:`video.duration`
      - :py:class:`datetime.timedelta`
      - The length of the video.

    * - :literal:`video.tags`
      - :py:class:`list[.Tag]`
      - List of video tags.

    * - :literal:`video.like`
      - :py:class:`int`
      - Likes amount of the video.

    * - :literal:`video.views`
      - :py:class:`int`
      - Number of views of the video.

    * - :literal:`video.hotspots`
      - :py:class:`list[int]`
      - Timestamps of the video hotspots. Used by Pornhub player to display hot moments.

    * - :literal:`video.date`
      - :py:class:`datetime.datetime`
      - The video publication date.

    * - :literal:`video.pornstars`
      - :py:class:`.User`
      - Pornstars in the video, represented as a list of :py:class:`.User` objects.

    * - :literal:`video.categories`
      - :py:class:`list[str]`
      - The video categories.
    
    * - :literal:`video.author`
      - :py:class:`.User`
      - The user account that posted the video.

    * - :literal:`video.id`
      - :py:class:`int`
      - The video ID, used internally by Pornhub. Not to be confused with the video viewkey.
    
    * - :literal:`video.watched`
      - :py:class:`bool`
      - Whether the video has been watched by the client (will not work in some cases).
    
    * - :literal:`video.is_free_premium`
      - :py:class:`bool`
      - Whether the video is part of Pornhub free premium plan (will not work in some cases).

    * - :literal:`video.preview`
      - :py:class:`.Image`
      - The small preview you see when hovering a video (will not work in some cases).
    
    * - :literal:`video.is_favorite`
      - :py:class:`bool`
      - Whether the video is set a favorite by the client.

    * - :literal:`video.is_HD`
      - :py:class:`bool`
      - Whether the video is available in a High Definition quality.
    
    * - :literal:`video.is_VR`
      - :py:class:`bool`
      - Whether the video is available in VR.

    * - :literal:`video.embed`
      - :py:class:`str`
      - The video embed URL, if you want to integrate it into a website.

.. warning::
  Some video properties (`preview`, `watched` and `is_free_premium`) are only available
  if the video comes from a :py:class:`.VideoQuery` because of the limited visibility of
  the data. You can use these properties by using :meth:`.Query.sample` and directly on the
  video object, although it is not recommended. 

  .. code-block:: python

    for video in query.sample(watched = True):
      print(video.title)
    # Is the same as
    for video in query.sample():
      if video.watched:
        print(video.title)
  
  If you absolutely need to access these properties outside of a query, you can turn on
  query emulation with `video.ALLOW_QUERY_SIMULATION = True`. This will create a fake query
  but is very slow and requires user authentication.

Interactions
------------

As of version 4.3, some interactions are available with the video:

.. list-table:: PHUB Video Interactions
    :header-rows: 1

    * - Method
      - Description

    * - :meth:`.Video.like`
      - Set or unset the video as liked.

    * - :meth:`.Video.favorite`
      - Set or unset the video as favorite.
    
    * - :meth:`.Video.watch_later`
      - Add or remove the video from the watch later playlist.

Refreshing data
---------------

Refreshing :py:class:`.Video` objects is done through the :meth:`.Video.refresh` method.

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
