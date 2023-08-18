'''
#### PHUB - An API wrapper.

See https://phub.rtfd.io for documentation.
'''

from phub import ( core, utils, consts, classes, parser )

# Shortcuts
from phub.core import Client
from phub.utils import Quality
from phub.classes import Video, User

# Debugging controls
from sys import stdout
from io import TextIOBase

def debug(boolean: bool, file: TextIOBase = stdout) -> None:
    '''
    Activate PHUB logs.
    
    Args:
        boolean (bool): Wether to set debug on.
        file (TextIO): File to send logs to (defaults: stdout).
    '''
    
    utils.DEBUG = boolean
    utils.DEBUG_FILE = file
    
    utils.log('init_', 'Switching logging to', boolean)

# EOF
