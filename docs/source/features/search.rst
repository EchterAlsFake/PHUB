Searching
=========

You can easily perform a research on Pornhub with :meth:`.Client.search`.

.. code-block:: python

    import phub

    client = phub.Client()
    query = client.search('my query')

Search filters
--------------

You can specify a lot of parameters to restrict your search.

.. code-block:: python

    import phub
    from phub.locals import *

    client = phub.Client()
    query = client.search('my query', category = 'french')

For instance, this query will be restrained to search in the French category.

.. warning::
  
    As of now, Pornhub only supports searching in one Category at a time.
    But you can still exclude as many as you want!

.. code-block:: python

    client.search(
        ...,
        category = 'french',
        exclude_category = ('bbw', 'german'),
        production = 'homemade'
    )

Using queries
-------------

When calling :meth:`.Client.search` or any other query method, nothing is actually
fetched. Instead, a :py:class:`.Query` is created. This object is responsible for
automatically managing the requests and caches to make the query as efficient as it
can be (hopefully).

Then, all you have to do is iterate it.

.. code-block:: python

    for video in query:
        print(video.title)

For more in-depth iteration, you can use the sample method.

.. code-block:: python

    # Fetch the 10 first videos
    for video in query.sample(max = 10):
        print(video.title)
    
    # Fetch only non watched
    for video in query.sample(watched = False):
        print(video.title)
    
    # Fetch by pages
    for page in video.pages:
        print(page)

To exploit video data, see :doc:`here </features/video>`.

Using different Query types while searching
-------------------------------------------

Alternatively, you can use the HubTraffic API from Pornhub.
It is faster and more reliable, but provides less information.

.. code-block:: python

    query = client.search_hubtraffic(...)

Refreshing queries
------------------

As of right now, queries cannot be refreshed. Instead, you need
to initialise a new query.

.. code-block:: python

  # Check search results once every 10 min

  args = dict(
    query = 'my query',
    category = 'french'
    # Other parameters if you want
  )

  while 1:

    # Initialise a new query
    query = client.search(**args)

    print(f'First result is: {query[0].title}!')

    time.sleep(60 * 10) # Wait 10 min
