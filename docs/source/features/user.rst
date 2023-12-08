Users
=====

:py:class:`.User` objects represents Pornhub users.

.. note:: There is a difference between Users and
    Account objects. :doc:`Accounts </features/account>` represents *your*
    account connected via PHUB. 

Exploiting data
---------------

Following data can be harvested from :py:class:`.User`
objects.

.. code-block:: python

    user = ...

    user.name   # The username
    user.url    # The link to the user page
    user.bio    # The user public biography (or None)
    user.info   # User data (relationship, orientation, etc.)
                # Warning: Changing the client language affect this.
    user.avatar # The user avatar as an phub.Image object.
    user.videos # Query containing the videos posted by the user.
    user.type   # The type of the user (model, channels, pornstar, users, etc.)

    # Only if the user is a pornstar
    user.uploads # Pornstar personnal uploads

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
        param = (Sort.USER_NEWEST
                 | Member.IS_ONLINE
                 | Member.HAS_AVATAR
                 | Member.OPEN_RELATION
                 | Member.GENDER_NON_BINARY)
    )

This method behaves like :meth:`.Client.search`: you can select custom filters for the
query:

.. code-block:: python

    # Member type
    Member.IS_MODEL
    Member.IS_STAFF
    Member.IS_ONLINE

    # Member content
    Member.HAS_AVATAR
    Member.HAS_VIDEOS
    Member.HAS_PHOTOS
    Member.HAS_PLAYLISTS
    Member.OFFER_FAN_CLUB
    Member.OFFER_CUSTOM_VIDEOS

    # Member relationship
    Member.SINGLE
    Member.TAKEN
    Member.OPEN_RELATION

    # Member gender
    Member.GENDER_MALE
    Member.GENDER_FEMALE
    Member.GENDER_COUPLE
    Member.GENDER_TRANS_FEMALE
    Member.GENDER_FEMALE_COUPLE
    Member.GENDER_TRANS_MALE
    Member.GENDER_NON_BINARY
    Member.GENDER_OTHER

    # Member interests
    Member.INTO_NONE
    Member.INTO_MALE
    Member.INTO_FEMALE
    Member.INTO_ALL

    # You can also use these sort filters    
    Sort.USER_POPULAR # Alongside with a sort period like SORT.week
    Sort.USER_NEWEST

Searching for pornstars
-----------------------

The :meth:`.Client.search_user` method only search for community members.
If you want to search specifically for pornstars, you can use the
:meth:`.Client.search_pornstar` method.

.. code-block:: python

    users = core.search_pornstar(name = 'Target',
                                 sort_param = ...)

There is no custom pornstar search filters in Pornhub, so the only filters
available are the sort params.

Note that the results will be a query containing :py:class:`.User` objects.
Their :attr:`.User.type` will be :literal:`'pornstar'`.

You can learn more about PHUB queries :dov:`here </features/search>`.