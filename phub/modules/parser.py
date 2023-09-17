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


def renew(video: Video) -> None:
    '''
    Attempt to renew the connection with Pornhub.
    
    Args:
        video (Video): The object that called the parser.
    '''
    
    # Get page JS code
    code = consts.re.get_rn_script(video.page)
    
    # Format JS code to python code
    code = consts.re.rm_comments(code)
    code = consts.re.format_rn_ifs(code)
    code = consts.re.format_rn_els(code)
    code = ''.join(code.split())
    code = consts.re.format_rn_var(code)
    code = code.replace('varn;', '').replace(';', '\n')
    
    # Execute code
    locales = {'n': 0, 'p': 0, 's': 0}
    exec(code, locales)
    n, p, s, _ = locales.values()
    n = utils.least_factors(p)
    
    # Build cookies
    end = consts.re.get_rn_cookie(video.page)
    cookie = f'{n}*{p / n}:{s}:{end}'
    
    # Inject cookie and reload page
    video.client.session.cookies.set('RNKEY', cookie)
    video.refresh()

def resolve(video: Video) -> dict:
    '''
    Resolves obfuscation that protects PornHub video M3U files.
    
    Args:
        video (Video): The object that called the parser.
    
    Returns:
        dict: A dictionary containing clean video data, fresh from PH.
    '''
        
    for _ in range(consts.MAX_VIDEO_RENEW_ATTEMPTS):
        
        response = consts.re.get_flash(video.page)
        
        if not response:
            renew(video)
            continue
        
        flash, ctx = response
        break
    
    else:
        raise errors.ParsingError('Max renew attempts exceeded.')
    
    # Load context
    return json.loads(ctx)

# EOF