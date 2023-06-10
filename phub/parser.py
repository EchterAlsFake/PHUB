'''
Parsing script for the PHUB package.
'''

import json
from phub import consts

def resolve(html: str) -> dict:
    '''
    Resolves obfuscation that hides PornHub video data.
    '''
    
    flash, ctx = consts.regexes.video_flashvar(html)[0]
    script = html.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    
    # Load context
    data: dict = json.loads(ctx)
    
    # Format the script
    script = ''.join(script.replace('var', '').split())
    script = consts.regexes.sub_js_comments('', script)
    script = script.replace(flash.replace('var', ''), 'data')
    
    # Execute the script
    exec(script)
    
    return data