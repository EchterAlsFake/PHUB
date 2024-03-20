Quick Start
===========

Installation
------------

PHUB uses the following dependencies:

- `requests`_
- `ffmpeg-progress-yield`_
- `click`_ (optional, used for the built-in CLI)

.. _requests: https://pypi.org/project/requests/
.. _click: https://pypi.org/project/click/
.. _ffmpeg-progress-yield: https://pypi.org/project/ffmpeg-progress-yield/

- Installing the lastest stable release (python 3.11 or higher):

.. code-block:: bash

    pip install --upgrade phub

- Installing the latest unstable updates (python 3.11 or higher):

.. code-block:: bash

    pip install --upgrade git+https://github.com/Egsagon/PHUB.git

- There also is a python 3.10 branch. Beware it might not be updated as often.

.. code-block:: bash

    pip install --upgrade git+https://github.com/Egsagon/PHUB.git@py-3.10

You can use PHUB as a :doc:`CLI </guides/cli-usage>`,
a :doc:`GUI </guides/gui-usage>` or a :doc:`Python package </guides/pkg-usage>`. 