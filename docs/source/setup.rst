Setting up PHUB
===============

.. note::

    You will need python **3.11**
    or higher.

To install PHUB, you can use pip:

.. code_block:: sh

    pip install phub

Or using the project directory
to get the latest features:

.. code_block:: sh

    pip install --upgrade git+https://github.com/Egsagon/PHUB.git

And just like that, the package is installed!
You can call it from the terminal to test it. 

.. code_block:: sh

    $ python -m phub
    Usage: python -m phub [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    download  Download a specific video.
    ui        Run in UI mode.

You can learn more about the built-in CLI :doc:`here<CLI>`.