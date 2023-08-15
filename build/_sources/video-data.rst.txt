Exploiting video data
=====================

Here are the most useful data properties of `.Video` objects.

.. note::
    All this data can be refreshed at once using :meth:`.Video.refresh`.

.. list-table:: List of cached video properties
    :header-rows: 1

    * - Property
      - Type
      - Description
    * - :attr:`~phub.Video.title`
      - :py:class:`str`
      - The original video title.
    * - :attr:`~phub.Video.image_url`
      - :py:class:`str`
      - The thumbnail image URL.
    * - :attr:`~phub.Video.is_vertical`
      - :py:class:`bool`
      - Wether the video is in vertical mode.
    * - :attr:`~phub.Video.duration`
      - :py:class:`~datetime.timedelta`
      - The video duration.
    * - :attr:`~phub.Video.tags`
      - :py:class:`list` of :class:`~phub.classes.Tag`
      - List of tags the video is referenced in.
    * - :attr:`~phub.Video.like`
      - :class:`~phub.classes.Like`
      - The up and down votes for the video.
    * - :attr:`~phub.Video.views`
      - :py:class:`int`
      - The video view amount.
    * - :attr:`~phub.Video.hotspots`
      - :py:class:`list` of :py:class:`int`
      - The video hotspots list (as provided by PH).
    * - :attr:`~phub.Video.date`
      - :class:`~datetime.datetime`
      - The video post date.
    * - :attr:`~phub.Video.author`
      - :class:`~phub.classes.User`
      - An object representing the video author.

Advanced usage
--------------

Getting upvotes and downvotes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    video = ...

    upvotes = video.like.up
    downvotes = video.like.down

    print(f'The video has {upvotes=} & {downvotes=}')

Downloading the video thumbnail
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import requests

    client = ...
    video = ...

    with open('thumbnail.png', 'wb') as file:

        # Get the image bytes
        b = requests.get(video.image_url).content

        # Alternatively, you can use directly the client
        # to make the request more legit
        # b = client._call('GET', video.image_url, simple_url = False).content

        file.write(b)
