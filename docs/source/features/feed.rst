Account feed
============

.. note::
    
    As of today, feed parsing is still experimental and requires bs4.

If a :py:class:`.Account` object initialises
successfully, you can access your account :py:class:`.Feed`.

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password')

    # Print the first 10 feed news
    for item in client.account.feed.sample(max = 10):
        print(item)

You can also specify custom feed filters:

.. code-block:: python

    from phub.locals import Section

    comments_feed = client.account.feed.filter(
        user = 'my-user', # Filter notifications from a specific user name or object
        section = Section.COMMENTS # Or any other section type
    )

    # Print the first 10 feed news
    for item in comments_feed.sample(max = 10):
        print(item)
