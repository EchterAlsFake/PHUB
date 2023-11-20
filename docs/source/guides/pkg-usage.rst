Package Usage
=============

Initialising a session
----------------------

First thing to do is setting up a client.
A client represents one connection to PH,
and you can use multiple at the same time.
You can also specify a custom language
locale (``en`` by default). This will
affect searching preferences, video titles,
etc.

.. code-block:: python

    import phub

    client = phub.Client(language = 'en')

Fetching a video
----------------

If you want to work with a specific video
you know the URL of, you can initialise it
like so:

.. code-block:: python

    import phub

    client = phub.Client()

    url = 'https://www.pornhub.com/view_video.php?viewkey=xxx'
    video = client.get(url) # (1)!

.. code-annotations::
    #.
        Note that you can also load the video 
        using the `viewkey` paramater in the URL.

        .. code-block:: python

            video = client.get(key = 'xxx')

Accessing data
--------------

A :py:class:`.Video` object has several properties you can use to fetch
data on a video. By default, no data is actually fetched until you call
a property for optimization purposes. Once fetched, data is cached for
each property. If you want to refresh the data, you will have to clear
the cache by calling :meth:``.Video.refresh``.

.. note::
  
  You can find out all the available properties
  in :doc:`downloading </features/video>`.

.. code-block:: python

    print(f'The "{video.title}" has {video.like.up} likes!')

You can check out all video properties in the :py:class:`.Video` API docs.

Downloading a video
-------------------

A video can be downloaded via :meth:`.Video.download`.

.. code-block:: python

    import phub
    from phub.locals import Quality

    video = ...

    video.download(path = 'my-video.mp4',
                   quality = Quality.BEST)

You can set the quality to be ``BEST``, ``HALF`` or ``WORST``, or an :py:class:`int`
for an absolute value.

.. note:: Tip: you can set the ``path`` paramater to be a directory for the video
    to be downloaded in. The file name will automatically be the video id. 

For advanced downloading, see :doc:`downloading </guides/download>`.

Debugging
---------

You can use Python `logging`_ library to debug your code and see what's wrong with
it or the API.

.. _logging: https://docs.python.org/3/library/logging.html

.. code-block:: python

    import phub
    import logging

    logging.BasicConfig(level = ...)

    client = phub.Client()
    ...

Compatibility
-------------

Most of the PHUB objects have a ``dictify`` method that allows
them to be converted to serialized objects.

.. warning::

  PHUB objects are often linked between each others (especially videos, images and users).
  Calling a ``dictify`` method on a object can make several other objects fetched, parsed
  and ``dictify``ed at the same time. You can manage this feature by specifying which keys
  are made into the response dictionnary using the ``keys`` parameter.  

This can be used with other languages as a shell command, and
as a server.

.. code-block:: python

    import phub
    import flask

    client = phub.Client()
    app = flask.Flask(__name__)

    @app.route('/get')
    def get():
        try:
            url = flask.request.args.get('video')
            video = client.get(url)
            res = video.dictify()
        
        except Exception as err:
            res = {'error': repr(err)}
        
        return flask.jsonify(res)

    if __name__ == '__main__':
        app.run()

For instance, this script will use flask to run a web server
that can fetch video data:

.. code-block:: bash

    $ curl <localhost>/get?video=abcdef1234
    {
        "name": "A cool video"
        # etc.
    }

Each ``dictify`` method can take as argument a :py:class`list[str]` of keys,
if you want to avoid fetching specific things.

For exemple, by default a serialized :py:class:`.User` object will also serialize
its avatar (:py:class:`.Image` object).

Below is a list of all serializeable PHUB objects, along with their keys and Special
keys (objects that require further fetching and seriadszddsfkation)

.. list-table:: Serializeable objects
    :header-rows: 1

    * - Object
      - Default keys
      - Special keys

    * - :py:class:`.Video`
      - ``url``, ``key``, ``is_vertical``, ``duration``, ``views``, ``date``, ``orientation``
      - ``image``, ``tags``, ``like``, ``pornstars``, ``categories``, ``author``
    
    * - :py:class:`.User`
      - ``name``, ``url``, ``type``, ``bio``, ``info``
      - ``avatar``

    * - :py:class:`.Image`
      - ``url``, ``name``, ``_servers``
      - /

    * - :py:cass:`.Account`
      - ``name``, ``avatar``, ``is_premium``
      - ``user``
    
    * - :py:class:`.Tag`
      - ``name``, ``count``
      - /
    
    * - :py:class:`.Like`
      - ``up``, ``down``, ``ratings``
      - /
    
    * - :py:class:`.FeedItem`
      - ``user``, ``header``, ``item_type``
      - /