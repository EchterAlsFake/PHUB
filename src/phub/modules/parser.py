from __future__ import annotations

import re

import json
import logging
from typing import TYPE_CHECKING

from .. import utils
from .. import errors
from .. import consts

if TYPE_CHECKING:
    from .. import Client
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
    region_blocked_regex = re.compile(r'<div\s+id=["\']js-player["\']\s+class=["\']videoGeoUnavailable["\']\s*>')
    if re.search(region_blocked_regex, video.page):
        raise errors.RegionBlocked

    flash, ctx = consts.re.get_flash(video.page)
    
    try:
        obj = json.loads(ctx)
        return obj
    
    except Exception:
        logger.error('Failed to parse flash %s for video %s', flash, video)
        raise errors.ParsingError('Failed to resolve page for', video)

def challenge(client: Client, challenge: str, token: str) -> None:
    '''
    Resolves a PH challenge.
    '''
    
    # Format code
    code = consts.re.parse_challenge(challenge)
    code = consts.re.ponct_challenge(code)
    code = '\n'.join(code.split(';'))
    
    # Execute code
    context = dict(p = 0, s = 0)
    exec(code, context)
    
    p = context['p']
    s = context['s']
    n = utils.least_factors(p)
    
    # Build and inject cookie
    cookie = f'{n}*{p // n}:{s}:{token}:1'
    client.session.cookies.set('KEY', cookie)
    logger.info('Injected cookie %s', cookie)

# EOF