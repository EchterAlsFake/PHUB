from __future__ import annotations

import json
import logging
import time
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
    flash, ctx = consts.re.get_flash(video.page)
    
    try:
        obj = json.loads(ctx)
        return obj
    
    except:
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
    logging.info(f"Sleeping for {consts.CHALLENGE_SLEEP} seconds")
    time.sleep(consts.CHALLENGE_SLEEP)
    cookie = f'{n}*{p / n}:{s}:{token}:1'
    client.session.cookies.set('KEY', cookie)
    logger.info('Injected cookie %s', cookie)
    

# EOF