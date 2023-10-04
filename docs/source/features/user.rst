Users
=====

:py:class:`.User` objects represents Pornhub users.

.. note:: There is a difference between Users and
    Account objects. Account represents *your*
    account connected via PHUB. 

Exploiting data
---------------

Following data can be harvested from :py:class:`.User`
objects.

.. code-block:: python

    user = ...

    user.name # The username
    user.url # The link to the user page

    user.bio # The user public biography (or None)

    user.info # User data (relationship, orientation, etc.)
    # Warning: Changing the client language affect this
    # dictionnary.

    user.avatar # The user avatar as an Image object.

    user.videos # Query containing the videos posted by the user.

Refreshing User data
--------------------

Refreshing this user data is done the same as other
refreshable objects:

.. code-block:: python

    user.refresh(page = True, data = True)

Searching for users
-------------------

You can search for user accounts on the platform using :meth:`.Client.search_users`.

.. code-block:: python

    members = client.search_users(
        username = 'user',
        param = (Sort.USER_NEWEST
                 | Member.IS_ONLINE
                 | Member.HAS_AVATAR
                 | Member.OPEN_RELATION
                 | Member.GENDER_NON_BINARY)
    )

This method behaves like :meth:`.Client.search`: you can select custom filters for the
query:

- Member type 

    .. code-block:: python

        Member.IS_ONLINE
        Member.IS_MODEL
        Member.IS_STAFF

- Member content

    .. code-block:: python

        Member.HAS_AVATAR
        Member.HAS_VIDEOS
        Member.HAS_PHOTOS
        Member.HAS_PLAYLISTS
        Member.OFFER_CUSTOM_VIDEOS
        Member.OFFER_FAN_CLUB

- Member relationship

    .. code-block:: python

        Member.SINGLE
        Member.TAKEN
        Member.OPEN_RELATION

- Member gender

    .. code-block:: python

        Member.GENDER_MALE
        Member.GENDER_FEMALE
        Member.GENDER_COUPLE
        Member.GENDER_TRANS_FEMALE
        Member.GENDER_FEMALE_COUPLE
        Member.GENDER_TRANS_MALE
        Member.GENDER_NON_BINARY
        Member.GENDER_OTHER

- Member interests

    .. code-block:: python

        Member.INTO_NONE
        Member.INTO_MALE
        Member.INTO_FEMALE
        Member.INTO_ALL

- You can also sort queries using these 2 sort filters:

    .. code-block:: python
        Sort.USER_POPULAR # Alongside with sort periods
        Sort.USER_NEWEST
