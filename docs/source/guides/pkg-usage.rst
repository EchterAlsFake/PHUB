Package Usage
=============

Initialising a session
----------------------

First thing to do is setting up a client.
A client represents one connection to PH,
and you can use multiple at the same time.
You can also specify a custom language
locale [1]_ (``en`` by default). This will
affect searching preferences, video titles,
etc.

Titles will by default be forced to change.
You can disable this behaviour, by setting
`change_title_language = off`.


You can also do a geo-bypass, although this hasn't
been tested well, so no guarantee.

set `bypass_geo_blocking = True`, this will fake your
IP and country, similar how youtube-dl does.

Aside from that, you can also switch between
webmaster and HTML parsing. Webmaster is the official
PornHub API, while HTML parsing fetches the
regular HTML page to extract data.

You can switch with: `use_webmaster_api = True` or False.

.. code-block:: python

    import phub

    client = phub.Client(language = 'de')




Proxy support is also possible, but only SOCKS5 protocol is supported. You need to apply the proxy in the
format "socks5://<ip>:<port>" and set it in the consts file. Here's an example:

.. code-block:: python
    import phub
    phub.consts.PROXY = "socks5://187.133.7.42:420"
    client = phub.Client() # This client has proxies enabled

NOTE:

There absolutely NO guarantee that this feature is perfectly functional. Your IP could always be leaked.

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
        using the `viewkey` parameter in its URL.

        .. code-block:: python

            video = client.get('xxx')

Accessing data
--------------

A :py:class:`.Video` object has several properties you can use to fetch
data on a video. By default, no data is actually fetched until you call
a property for optimization purposes. Once fetched, data is cached for
each property. If you want to refresh the data, you will have to clear
the cache by calling :meth:`.Video.refresh`.

.. note::
  
  You can find out all the available properties
  in the :doc:`video docs </features/video>` or in the :py:class:`.Video` class.

.. code-block:: python

    video = client.get('xxx')

    print(f'The "{video.title}" has {video.likes.up} likes!')

Downloading a video
-------------------

A video can be downloaded by using :meth:`.Video.download`.

.. code-block:: python

    import phub
    from phub.locals import Quality

    client = phub.Client()
    video = client.get('xxx')

    video.download(path = 'my-video.mp4',
                   quality = Quality.BEST)

.. note::
  
  Tip: You can set the ``path`` parameter to be a directory for the video
  to be downloaded in. The file name will automatically be the video id. 

For more information on how to download, see :doc:`downloading </guides/download>`.

Logging
-------

You can use Python `logging`_ library to debug your code and see what's wrong with
it or the API.

.. _logging: https://docs.python.org/3/library/logging.html

.. code-block:: python

    import phub
    import logging

    # Use whatever configuration you want
    logging.BasicConfig(level = logging.INFO)

    client = phub.Client()
    ...

Compatibility
-------------

Most of the PHUB objects have a ``dictify`` method that allows
them to be converted to serialized objects.

.. code-block:: python

  import phub

  client = phub.Client()
  video = client.get('xxx')

  data = video.dictify()

Result: ``{"name": "A cool video", ...}``

This is done for compatibility and ease of use with other
languages and applications, since you can easily run a small python
script or local server:

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
            res = { 'response': video.dictify() }
        
        except Exception as err:
            res = { 'error': repr(err) }
        
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

Each ``dictify`` method can take as argument a :py:class:`list[str]` of keys,
if you want to avoid fetching specific things.

Below is a list of all serializable PHUB objects, along with their keys.
"PHUB objects" are keys that redirect to a PHUB object.

.. list-table:: Serializable objects
    :header-rows: 1

    * - Object
      - Default keys
      - PHUB objects

    * - :py:class:`.Video`
      - ``id``, ``title``, ``is_vertical``, ``duration``, ``orientation``, ``orientation``, ``views``, ``hotspots``, ``date``, ``is_free_premium``, ``is_HD``, ``is_VR``, ``embed``, ``liked``, ``watched``, ``is_favorite``
      - ``image``, ``tags``, ``likes``, ``pornstars``, ``categories``, ``author``, ``preview``
    
    * - :py:class:`.User`
      - ``name``, ``url``, ``type``, ``bio``, ``info``
      - ``avatar``

    * - :py:class:`.Image`
      - ``url``, ``name``, ``_servers``
      - /

    * - :py:class:`.Account`
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

By default, PHUB object keys will appear as ``repr`` strings, unless
you allow it with ``object.dictify(recursive = True)``.

.. warning::

  Turning on recursion can make PHUB open more requests that you might
  actually need. Make sure you specify only the keys you need when using it.

.. [1] Supported language locales are: ``cn``, ``de``, ``fr``, ``it``, ``pt``, ``pl``, ``rt``, ``nl``, ``cz``, ``jp``
