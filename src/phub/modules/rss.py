from __future__ import annotations
from xml.etree import ElementTree
from typing import Iterator, TYPE_CHECKING
from .. import consts
if TYPE_CHECKING:
    from .. import Client, Video
_RSS = None


def get(client=None):
    """
    Get and parse the RSS flux.

    Note: you may want to ignore the first element.
    """
    from .. import Client
    from ..objects import Video
    global _RSS
    _RSS = client or _RSS or Client()
    res = _RSS.call(consts.RSS)
    tree = ElementTree.fromstring(res.content)
    for item in tree.iter('item'):
        obj = Video(client=_RSS, url=item.find('link').text)
        obj.data['data@title'] = item.find('title').text
        obj.data['data@duration'] = item.find('duration').text
        obj.data['data@thumb'] = item.find('thumb').text
        yield obj
