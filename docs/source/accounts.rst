Accounts handling
=================

PHUB supports account connection.
You can connect to your own account with your username and password like so:

.. code-block:: python

    import phub

    client = phub.Client(username = 'my-username',
                         password = 'my-password')

.. note:: Your credentials won't be saved nor send to any servers except Pornhub.

You can also enter them in a json file and initialise the client with it:

creds.json:

.. code-block:: json

    {
        "username": "my-username",
        "password": "my-password"
    }

.. code-block:: python

    import phub

    client = phub.Client.from_file('creds.json')

.. default-literal-role:: python

By default, the client will immediatly attempt to login. This can be disabled by setting :literal:`autologin=False` 
If the login was successfull, you can access some features of your account:

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password')

    # Get recommended videos
    client.account.recommended

    # Get video history
    client.account.watched

    # Get liked videos
    client.account.liked

If you want to login later, you can do something like:

.. code-block:: python

    import phub

    client = phub.Client('my-username', 'my-password', autologin = False)

    # Do things...

    client.login()

You can also use :meth:`.Client.login` to refresh your connection.

Here is an exemple script that allows you to download the last 10 videos you watched:

.. code-block:: python

    import phub
    from phub import Quality

    client = phub.Client(...)
    client.login()

    for video in client.account.watched[:10]:
        video.download('.', quality = Quality.BEST)

.. note::
    There is a difference between `Account` and `User` objects. The first represents *your* account,
    the one linked with the phub client, while the 2nd represent any PH user.

    To get your `User` object (e.g., to get your posted videos), you can do something like this:
    :literal:`client.get_user(name = client.account.name)`

Accessing the user videos
-------------------------

The following queries are available through the user account:

.. code-block:: python

    client = phub.Client('my-username', 'my-password')

    account = client.account # (1)!

.. code-annotations::
    #. The :attr:`~.core.account` attribute will be :literal:`None` if the login fails.


Fetching the user feed
----------------------

There is also an experimental feature that allows you to get the content of your feed:

.. warning:: This feature is currenlty not stable, but is under development.

.. code-block:: python

    import phub
    from phub.consts import FeedType

    client = ...

    feed = client.account.feed

    # Enumerate feed events
    for event in feed:

        if event.type is FeedType.ACHIEVEMENT:
            print('You got a new achievement!', event.content)

        if event.type is FeedType.UPLOAD:
            print('Someone you follow posted a new video:', event.url)

        # etc.