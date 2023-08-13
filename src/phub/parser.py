'''
### Parsing script for the PHUB package. ###
'''

from __future__ import annotations

import json
import js2py
from phub import consts
from phub.utils import log

from typing import TYPE_CHECKING
if TYPE_CHECKING: from classes import Video

RENEW_MAX_ATTEMPTS = 3

def renew(video: Video) -> None:
    '''
    Attempt to renew the connection with Pornhub.
    
    Args:
        video (Video): The object that called the parser.
    '''
    
    # Fetch numbers
    log('parse', 'Attempting to renew connection')
    script, end = consts.regexes.video_renew_connect(video.page)[0]
    n, p, s = js2py.eval_js(script + ';return [n, p, s];}')()
    
    # Build the cookie
    cookie = f'{n}*{p / n}:{s}{end}'
    log('parse', 'Injecting calculated cookie:', cookie)
    
    # Send cookie and reload page
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
    
    log('parse', 'Resolving page JS script...', level = 5)
    
    for i in range(RENEW_MAX_ATTEMPTS):
        
        response = consts.regexes.video_flashvar(video.page)
        
        if not len(response):
            renew(video)
            continue
        
        flash, ctx = response[0]
        break
    
    else:
        raise consts.ParsingError('Max renew attempts exceeded.')
    
    script = video.page.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    log('parse', 'Formating flash:', flash, level = 5)
    
    # Load context
    data: dict = json.loads(ctx)
    
    # Format the script
    script = ''.join(script.replace('var', '').split())
    script = consts.regexes.sub_js_comments('', script)
    script = script.replace(flash.replace('var', ''), 'data')
    
    # Execute the script
    exec(script) # In case you ask, what we are doing here is converting the obfuscated Pornhub JS code into python code so that we can execute it and directly get the video M3U file.
    log('parse', 'Execution successful, script resolved', level = 5)
    
    return data

# EOF