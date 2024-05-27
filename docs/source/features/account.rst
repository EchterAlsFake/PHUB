Account object
==============

Using a client to login
-----------------------

.. warning::

    None of your data is being saved by PHUB.
    It only sends your credentials to the official Pornhub
    servers. Fore more information, have a look at the source `code`_.

.. _code: https://github.com/Egsagon/PHUB 

You can use the :py:class:`.Client` object to login
to some Pornhub account:

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password')

By default, PHUB will immediately attempt a login to Pornhub.
If you want to disable this behavior, set ``login`` to False.

.. code-block:: python

    import phub

    client = phub.Client('my-username',
                         'my-password',
                         login = False)

    # Login manually
    client.login()

Whether you decide to connect or not, an :py:class:`.Account` object
will be created at `client.account`. This is where you will be able
to view account related data.

If you did not enter credentials, this object won't be created.

Accessing data
--------------

Once a client is logged in, the following data is available:

.. code-block:: python

    client.account.name # The account name
    client.avatar # The account user avatar as an phub.Image object.
    client.is_premium # Whether the account has premium enabled.

    client.user # Public representation of the account. This is useful
                # if you want to access your own account's data/videos.

Account Queries
---------------

.. note::
    
    For more information on how to use PHUB Queries, see :doc:`searching </features/search>`.

Theses queries emit :py:class:`.Video` objects and are refreshable with :meth:`.Account.refresh`. 

* Recommended videos (:literal:`client.account.recommended`)

* Liked videos (:literal:`client.account.liked`)

* Video history (:literal:`client.account.watched`)

Here is an example on how to view your account history.

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password')

    history_length = 40

    for video in client.account.watched:
        print(f'Video {video.key} - "{video.title}"')

Accessing the feed
------------------

The account feed is accessible through :py:obj:`.Account.feed`.

You can learn more about the feed :doc:`here </features/feed>`.
