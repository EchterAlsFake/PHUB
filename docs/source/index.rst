PHUB documentation
==================

..
    Note - This documentation format is
    mostly stolen from bain3/pronotepy
    because i don't know how to write RST.

.. image:: images/banner.jpg
    :align: center

Introduction
^^^^^^^^^^^^

PHUB is an API wrapper for Pornhub (PH).
It is able to communicate with most used PH
features such as video searching, downloading,
account connection, etc.

.. note:: **Early dev** + i don't plan to
    maintain this often so don't hesitate
    to submit issues or requests through the
    project's `github page`_.

.. _github page: https://github.com/Egsagon/PHUB

Dependencies
^^^^^^^^^^^^

* ``requests``
* ``click``
* ``tqdm``

.. note:: Disclaimer: This project is probably
    against Pornhub TOS. Use at your own risks.

Guides
------

.. toctree::

    quickstart
    cli
    searching
    accounts

API docs
--------

.. toctree::

    api/index

.. autoclass:: phub.Client
