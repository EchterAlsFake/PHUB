'''
PHUB 4 parser.
'''

from __future__ import annotations

import json

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..objects import Video

from .. import utils
from .. import errors
from .. import consts


def resolve(video: Video) -> dict:
    '''
    Resolves obfuscation that protects PornHub video M3U files.
    
    Args:
        video (Video): The object that called the parser.
    
    Returns:
        dict: A dictionary containing clean video data, fresh from PH.
    '''
    
    # NOTE - Removed de-obfuscation script because it was deleted by PH
    # and we don't need it anymore
    
    # NOTE - Removed renew functionnality because it is no more raised
    # by PH for some reason.
    
    flash, ctx = consts.re.get_flash(video.page)
    
    return json.loads(ctx)

# EOF