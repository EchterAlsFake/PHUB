Account feed
============

If an :py:class:`.Account` objects initialises
successfully, you can access your account feed.

.. note::
    Pornhub's feed is the place where you get the
    notifications from your subscribtions, comments,
    video uploads, etc.

The :py:class:`.Feed` object is a utility object that
initialises custom :py:class:`.Query` objects. These
queries contain :py:class:`.FeedItem` objects.

You can get the raw feed this way:

.. code-block:: python

    my_feed = client.account.feed.feed

    for item in my_feed:
        print(item)

You can also specify custom filters to generate other
feeds queries.

.. code-block:: python

    from phub.locals import Section

    my_feed = client.account.feed.filter(
        user = 'my-user', # Filter notifications from a specific user name or object
        section = Section.COMMENTS # Or any other section type
    )

    for item in my_feed:
        print(item)
