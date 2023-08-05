CLI USage
=========

PHUB comes packaged with a built-in
command-line tool. You can access it
by calling the module from the terminal:

.. code-block:: bash

    $ python -m phub
    Usage: python -m phub [OPTIONS] COMMAND [ARGS]...

    Options:
        --help  Show this message and exit.

    Commands:
        download  Download a specific video.
        ui        Run in UI mode.

Downloading a video
-------------------

You can simply download a video using the
``download`` command:


.. code-block:: bash

    $ python -m phub download --url https://www.pornhub.com/view_video.php?viewkey=xxx

You can also specify a custom video quality and
output file:

.. code-block:: bash

    $ python -m phub download --url https://www.pornhub.com/view_video.php?viewkey=xxx \
                              --quality 1080 \
                              --output my-video.mp4

The given command will download the video with a quality of
1080p under the ``my-video.mp4``` filename.

Using the UI
------------

The CLI can also start a (very) barebone
UI. It is not really useful since it does not
hav a lot of features yet.

.. note:: You will need Tkinter to be installed

.. code-block:: bash

    $ python -m phub ui

.. image:: images/ui.png

Other features
--------------

Some features like searching for videos are
still to be implemented to the CLI.