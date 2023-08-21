'''
Parser script for the PHUB package.
'''

from __future__ import annotations

import json
from phub import consts
from phub import errors
from phub.utils import log, least_factors, hard_strip

from typing import TYPE_CHECKING
if TYPE_CHECKING: from classes import Video

RENEW_MAX_ATTEMPTS = 3

def renew(video: Video) -> None:
    '''
    Attempt to renew the connection with Pornhub.
    
    Args:
        video (Video): The object that called the parser.
    '''
    
    log('parser', 'Attempting to renew connection', level = 2)
    
    # Get page JS code
    code = consts.regexes.renew.script(video.page)[0]
    
    # Format JS code to python code
    code = consts.regexes.renew.comment('', code)
    code = consts.regexes.renew.states1(r'\n\g<1>:\n\t', code)
    code = consts.regexes.renew.states2(r'\n\g<1>:\n\t', code)
    code = hard_strip(code, '')
    code = consts.regexes.renew.variables(r'\g<1>=\g<2>\n', code)
    code = code.replace('varn;', '').replace(';', '\n')
    
    # Execute code
    locales = {'n': 0, 'p': 0, 's': 0}
    exec(code, locales)
    n, p, s, _ = locales.values()
    n = least_factors(p)
    
    # Build cookies
    end = consts.regexes.renew.cookie_end(video.page)[0]
    cookie = f'{n}*{p / n}:{s}:{end}'
    log('parser', 'Injecting calculated cookie:', cookie, level = 6)
    
    # Inject cookie and reload page
    video.client.session.cookies.set('RNKEY', cookie)
    video.refresh()

def resolve(video: Video) -> dict:
    '''
    Resolves obfuscation that protect PornHub video M3U files.
    
    Args:
        video (Video): The object that called the parser.
    
    Returns:
        dict: A dictionnary containing clean video data, fresh from PH.
    '''
    
    log('parser', 'Resolving page JS script...', level = 6)
    
    for _ in range(RENEW_MAX_ATTEMPTS):
        
        response = consts.regexes.video_flashvar(video.page)
        
        if not len(response):
            renew(video)
            continue
        
        flash, ctx = response[0]
        break
    
    else:
        raise errors.ParsingError('Max renew attempts exceeded.')
    
    script = video.page.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    log('parser', 'Formating flash:', flash, level = 6)
    
    # Load context
    data: dict = json.loads(ctx)
    
    # Format the script
    script = ''.join(script.replace('var', '').split())
    script = consts.regexes.sub_js_comments('', script)
    script = script.replace(flash.replace('var', ''), 'data')
    
    # Execute the script
    exec(script) # In case you ask, what we are doing here is converting the obfuscated Pornhub JS code into python code so that we can execute it and directly get the video M3U file.
    log('parser', 'Execution successful, script resolved', level = 6)
    
    return data

# EOF