.. image::
    https://github.com/Egsagon/PHUB/blob/master/assets/banner.png
    :align: center

==========================
PHUB - An API for PornHub.
==========================

PHUB is an API wrapper for Pornhub (PH).
It is able to communicate with most used PH
features such as video searching, downloading,
account connection, etc.

Learn more on the project `documentation`_ and
`github page`_.

.. _documentation: https://phub.readthedocs.io
.. _github page: https://github.com/Egsagon/PHUB

Installation
^^^^^^^^^^^^

Dependencies: ``requests``, ``click``, ``tqdm``

Install: ``pip install -U phub``
Or (dev) ``pip install -U git+https://github.com/Egsagon/PHUB.git``

Quick usage
^^^^^^^^^^^

.. code-block:: python

    import phub

    client = phub.Client()

    video = client.get(url = '...')
    video.download('my-video.mp4', quality = 'best')
