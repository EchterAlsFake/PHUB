Searching
=========

.. warning::

    The search feature might give inacurate results.
    I don't know yet why.

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
    for video in query[:10]:
        print(video.title)
    
    # Iterate through all videos 
    for video in query:
        print(video.title)

.. note:: Unlike :meth:`.Client.get`, by default the content
    of the video is not fetched yet, unless you ask for it
    (by calling `video.title` for example).

Search filters
--------------

PHUB support filtering queries like on the PH website.

.. automethod:: phub.core.Client.search

Category object
^^^^^^^^^^^^^^^

Categories objects are concatenable, e.g.:

.. code-block:: python

    from phub import Category

    # Represents both french and german categories
    my_category = Category.FRENCH | Category.GERMAN

    query = client.search(exclude_category = my_category) # (1)!

.. code-annotations::
    #. Pornhub doesn't support searching through multiple categories at once, so you can use this feature only with :atth:`exclude_category` and not :attr:`category`.
