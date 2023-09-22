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
