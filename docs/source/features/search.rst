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
You can see `here </api/locals>` a list of possible filters.

.. code-block:: python

    import phub
    from phub.locals import *

    client = phub.Client()
    query = client.search('my query', Category.FRENCH)

For instance, this query will be restrained to search in the French category.

You can use multiple Parameters objects by adding or substracting them, e.g.:

.. code-block:: python

    # Search in the French category for homemade production
    client.search(..., Category.FRENCH + Production.HOMEMADE)

    # Search for professional production, but exclude all BBW videos
    client.search(..., Production.PROFESSIONAL - Category.BBW)

    # Search for everything but BBW
    client.search(..., -Category.BBW)

.. warning:: As of now, Pornhub only supports searching in one Category at a time.
    But you can still exclude as many as you want!

Exploiting search results
-------------------------

When calling :meth:`.Client.search`, nothing is actually fetched. Instead, a
:py:class:`.Query` is created. This object is responsible for automatically managing
the search requests and caches to make it as efficient as it can be.

You can access its content directly using list item syntax, or :meth:`.Query.get`.

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

Using different Query types
---------------------------

There can be different subclasses of :py:class:`.Query`, which
have their own usage. For exemple:

.. list-table:: Query types
    :header-rows: 1

    * - Object
      - Page length
      - Description

    * - :py:class:`.Query`
      - Unknown
      - Base class for all queries. Responsible for handling item distribution. 

    * - :py:class:`.JQuery`
      - 30 
      - The default Query for searching. It uses the HubTraffic API to fetch data faster.
    
    * - :py:class:`.HQuery`
      - 32
      - Web-scrapper equivalent of :py:class:`.JQuery`. It provides the most accurate results.
    
    * - :py:class:`.FQuery`
      - 14
      - Query dedicated to the :py:class:`.Feed` object.

    * - :py:class:`.MQuery`
      - Unknown
      - Query dedicated to search for users.

    * - :py:class:`.UQuery`
      - 40
      - Query dedicated to search for videos on a user page.

While searching, you can use either :py:class:`.JQuery` or :py:class:`.HQuery`
(or your own :py:class:`.Query` subclass).

Note that :py:class:`JQuery` is faster because it fetches less data,
but it also *probably* use a different algorithm than :py:class:`.HQuery`,
which is more accurate but slower.

.. warning:: As of now, HQueries don't obey well to their parameters.
    You might prefer to use JQueries.

You can specify which one to use with the ``feature`` argument:

.. code-block:: python

    query = client.search(..., feature = phub.HQuery)

Refreshing queries
------------------

Queries are not meant to be refresh.
I mean, they can be refreshed by cleaning their cache,
but it might lead to misunderstandings so the best
way to refresh a query is to make another one.

.. code-block:: python

  # Check search results once every 10 min

  args = dict(
    query = 'my query',
    filter = Category.FRENCH # Or every filter you want
    # Other parameters if you want
  )

  while 1:

    # Initialise a new query
    query = client.search(**args)

    print(f'First result is: {query[0].title}!')

    time.sleep(60 *10) # Wait 10 min

