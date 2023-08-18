Long term usage
===============

Refreshing videos
-----------------

:py:class:`.Video` objects can be refreshed using the :meth:`.Video.refresh` method.
Once called, Every video property will be reloaded.

For exemple, this script will display the evolution of a video views each hour. 

.. code-block:: python

    import phub
    import time

    client = phub.Client()
    video = client.get('...')

    while 1:

        print(video.views)
        time.sleep(3600)
        video.refresh()

Refreshing queries
------------------

Queries are not meant to be refreshed, instead you can either refresh one of its output, or restart a new query.

For exemple, to get the first video of a query every hour:

.. code-block:: python

    import phub
    import time

    client = phub.Client()

    while 1:

        query = client.search('...')
        print(query[0])
        time.sleep(3600)

Refreshing the feed
-------------------

TODO

Refreshing client connection
----------------------------

TODO