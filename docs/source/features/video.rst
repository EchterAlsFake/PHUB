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

    * - :literal:`video.id`
      - The video internal id. Most likely to be used in Pornhub's databases.
    
    * - :literal:`video.watched`
      - Whether the video has been watched by the client.
    
    * - :literal:`video.is_free_premium`
      - Whether the video is part of Pornhub free premium plan.

    * - :literal:`video.preview`
      - The small preview you see when hovering a video, as a :py:class:`.Image` object.
    
    * - :literal:`video.is_favorite`
      - Whether the video is set a favorite by the client.

    * - :literal:`video.is_HD`
      - Whether the video is available in a High Definition quality.
    
    * - :literal:`video.is_VR`
      - Whether the video is available in VR.

    * - :literal:`video.id`
      - The internal video ID, used for API calls (different than the viewkey).
    
    * - :literal:`video.embed`
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
