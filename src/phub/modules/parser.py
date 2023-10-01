from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from .. import errors
from .. import consts

if TYPE_CHECKING:
    from ..objects import Video

logger = logging.getLogger(__name__)


def resolve(video: Video) -> dict:
    '''
    Resolves obfuscation that protects PornHub video M3U files.
    
    Args:
        video (Video): The object that called the parser.
    
    Returns:
        dict: A dictionary containing clean video data, fresh from PH.
    '''
    
    # NOTE - Keeping this in a separate file in case PH adds
    # more obfuscation stuff
    
    logger.info('Resolving %s page', video)
    flash, ctx = consts.re.get_flash(video.page)
    
    try:
        obj = json.loads(ctx)
        return obj
    
    except:
        logger.error('Failed to parse flash %s for video %s', flash, video)
        raise errors.ParsingError('Failed to resolve page for', video)

# EOF