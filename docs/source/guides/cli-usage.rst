CLI Usage
=========

PHUB comes with a built-in CLI with the most useful features.

.. code-block:: bash

    $ python -m phub

.. code-block:: bash

    Usage: python -m phub [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    download     Download a specific video.
    liked        Download the n-last watched videos.
    search       Search for videos.
    user-videos  Download the n last videos from a channel/model/etc.
    watched      Download the n-last watched videos.

Available features
------------------

.. warning:: When downloading multiple videos at the same time, do not input a
    file path in ``--output``, otherwise videos will overwrite themselves.


- Downloading a single video

    .. code-block:: bash
        
        $ python -m phub download <url> --quality <quality> --output <directory>

    ``URL`` can be the video URL/viewkey, or the path of a ``.txt`` file
    containing a list of URLs/viewkeys.

- Searching for videos

    .. code-block:: bash

        $ python -m phub search <query> --pages <int>

    Will search for videos and display their title, viewkey and duration.

    Example:

    .. code-block:: bash

        $ python -m phub search cum

        * Fucking My StepCousin (Creampie) After His Cock Got Hard Coz Showered Together - Xreindeers (0:19:27) - 64a52441300f4
        * A Beautiful Stranger From Paris Lets Me Taste  Her Croissant (0:11:19) - 64d6e71e75f61
        * my tiny pussy make him cum 3 times and once creampie ♡ (0:10:11) - ph630157542f70f
        * Кончил в сводную сестрёнку пока дома гости (0:10:02) - 649dc5ca2e7d0
        [...]

- Download watched videos

    .. code-block:: bash

        $ python -m phub watched --user <name> -n <int> --output <dir> --quality <video quality>

    Download the ``n`` last videos from the user history.
    You will be prompted for a username and a password.

- Download liked videos
    
    .. code-block:: bash

        $ python -m phub liked --user <name> -n <int> --output <dir> --quality <video quality>

    Download the ``n`` last liked videos.
    You will be prompted for a username and a password.

- Download videos from a user

    .. code-block:: bash

        $ python -m phub user_videos <username> -n <int> --output <dir> --quality <video quality>

    Download the ``n`` last liked videos.

- Update PHUB constants

    PHUB uses a constant system that can be updated locally.

    .. code-block:: bash

        $ python -m phub update_locals
    
    .. warning:: This will override a section of ``$PHUB/locals.py``
