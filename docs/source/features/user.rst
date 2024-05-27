Users
=====

:py:class:`.User` objects represents Pornhub users.

.. important:: There is a difference between Users and
    Account objects. :doc:`Accounts </features/account>` represents *your*
    account connected via PHUB. 

Exploiting data
---------------

Following data can be harvested from :py:class:`.User`
objects.

.. code-block:: python

    user = client.get(...)

    user.name    # The username
    user.url     # The link to the user page
    user.bio     # The user public biography (or None)
    user.info    # User data (relationship, orientation, etc.)
                 # Warning: Changing the client language affect this.
    user.avatar  # The user avatar as an phub.Image object.
    user.videos  # Query containing the videos posted by the user.
    user.type    # The type of the user (model, channels, pornstar, users, etc.)
    user.uploads # if user is a Pornstar, stores the personal uploads

Refreshing User data
--------------------

Refreshing this user data is done the same as other
refreshable objects, with :meth:`.User.refresh`.

Searching for users
-------------------

You can search for user accounts on the platform using :meth:`.Client.search_user`.

.. code-block:: python

    members = client.search_user(
        username = 'user',
        sort = 'newest',
        online = True,
        gender = 'non binary'
    )

This method behaves like :meth:`.Client.search`: you can select custom filters for the
query.
You can learn more about PHUB queries :doc:`here </features/search>`.
