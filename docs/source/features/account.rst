Account object
==============

Using a client to login
-----------------------

You can use the :py:class:`phub.Client` object to login
to some Pornhub account:

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password')

By default, PHUB will immediatly attempt a login to Pornhub.
If you want to disable this behavior, set ``login`` to False.

.. code-block:: python

    import phub

    client = phub.Client(
        'my-username',
        'my-password',
        login = False
    )

    # Login afterwards
    client.login()

If you created an account while specifying some credentials,
wether you enabled login or not, an :py:class:`phub.Account`
object will be created and connected to the :py:class:`phub.Client`.

If that is not the case, The :py:class:`phub.Account` object will
evaluate to :py:class:`None`.

Accessing data
--------------

The following account data is available:

.. code-block:: python

    client.account.name # The account name
    client.avatar # The account user avatar as an Image object.
    client.is_premium # Wether the account has premium enabled.

    client.user # Public representation of the account
    # This is useful if you want to access your own account's
    # videos or infos.

Account Queries
---------------

The following Queries are created and cached by :py:class:`phub.Account`.
(Refreshable with :literal:`client.account.refresh()` of course)

* Recommended videos (:literal:`client.account.recommended`)

* Liked videos (:literal:`client.account.liked`)

* Video history (:literal:`client.account.watched`)

All those queries behave like :doc:`normal search queries </features/search>`.

Accessing the feed

The feed is accessible through :literal:`client.account.feed`.

You can learn more about the feed :doc:`here </features/feed>`.
