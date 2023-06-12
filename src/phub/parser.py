'''
### Parsing script for the PHUB package. ###
'''

import json
from phub import consts
from phub.utils import log

def resolve(html: str) -> dict:
    '''
    #### Resolves obfuscation that protect PornHub video M3U files. ####
    --------------------------------------------------------------------
    
    Arguments:
    - `html` -- The raw HTML file of the video.
    
    --------------------------------------------------------------------
    Returns a `dict` object containing un-obsucated video data.
    '''
    
    log('parse', 'Resolving page JS script...', level = 5)
    flash, ctx = consts.regexes.video_flashvar(html)[0]
    script = html.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    log('parse', 'Formating flash:', flash, level = 5)
    
    # Load context
    data: dict = json.loads(ctx)
    
    # Format the script
    script = ''.join(script.replace('var', '').split())
    script = consts.regexes.sub_js_comments('', script)
    script = script.replace(flash.replace('var', ''), 'data')
    
    # Execute the script
    exec(script)
    log('parse', 'Execution successful, script resolved', level = 5)
    
    return data