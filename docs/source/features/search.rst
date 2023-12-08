Searching
=========

You can easily perform a research on Pornhub with :meth:`.Client.search`.

.. code-block:: python

    import phub

    client = phub.Client()
    query = client.search('my query')

Search filters
--------------

You can specify search filters by adding :py:class:`.Param` objects.
There is a list of constant Parameters you can import from ``phub.locals``.
You can see :doc:`here </api/locals>` a list of possible filters.

.. code-block:: python

    import phub
    from phub.locals import *

    client = phub.Client()
    query = client.search('my query', Category.FRENCH)

For instance, this query will be restrained to search in the French category.

You can use multiple Parameters objects by adding or subtracting them, e.g.:

.. warning::
  
    As of now, Pornhub only supports searching in one Category at a time.
    But you can still exclude as many as you want!

.. code-block:: python

    # Search in the French category for homemade production
    client.search(..., Category.FRENCH | Production.HOMEMADE)

    # Search for professional production, but exclude all BBW videos
    client.search(..., Production.PROFESSIONAL - Category.BBW)

    # Search for everything but BBW
    client.search(..., -Category.BBW)

Using queries
-------------

When calling :meth:`.Client.search` or any other query method, nothing is actually
fetched. Instead, a :py:class:`.Query` is created. This object is responsible for
automatically managing the requests and caches to make the query as efficient as it
can be (hopefully).

You can access its content directly using python list item syntax, or :meth:`.Query.get`.

.. code-block:: python

    item = query[0]
    # Or
    item = query.get(0)

You can also use it as a generator to get multiple videos:

.. code-block:: python

    # Fetch first 10 videos
    for video in query[0:10]:
        print(video.title)
    
    # Fetch every videos
    for video in query:
        print(video.title)

To exploit video data, see :doc:`here </features/video>`.

Using different Query types while searching
-------------------------------------------

With searching only, you can choose to use 2 different queries subclasses.
You should choose which one to use depending on what you want to do.

.. code-block:: python

    import phub

    client = phub.Client()

    # JSONQuery (recommended, uses HubTraffic) - faster, but less data
    query = client.search(..., feature = phub.JSONQuery)

    # HTMLQuery - slower, but fetches all of the video data
    query = client.search(..., feature = phub.HTMLQuery)

Refreshing queries
------------------

As of right now, queries cannot be refreshed. Instead, you need
to initialise a new query.

.. code-block:: python

  # Check search results once every 10 min

  args = dict(
    query = 'my query',
    filter = Category.FRENCH # Or/and any filter you want
    # Other parameters if you want
  )

  while 1:

    # Initialise a new query
    query = client.search(**args)

    print(f'First result is: {query[0].title}!')

    time.sleep(60 * 10) # Wait 10 min
