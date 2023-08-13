Searching
=========

One feature of PHUB is that it is able to
send and receive queries.

.. code-block:: python

    import phub

    client = phub.Client()

    # Create a custom query
    query = client.search('minecraft speedrun')

This query is a :class:`.Query` object.
It behaves like a list while being a generator,
which means it will only fetch the asked videos
if needed. You can access its content like so:

.. code-block:: python

    # Get a specific video
    first_video = query[0]

    # Iterate through a range of videos
    for video in query.range(0, 10):
        print(video.title)
    
    # Iterate through *all* videos
    # Warning: can be quite suspicious and detectable
    # by PH if there are a lot of videos. 
    for video in query:
        print(video.title)

.. note:: Unlike :meth:`.Client.get`, by default the content
    of the video is not fetched yet, unless you ask for it
    (by calling ``video.title`` for example).
