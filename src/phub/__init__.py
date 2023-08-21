'''
#### PHUB - An API wrapper for Pornhub.

See https://phub.rtfd.io for documentation.
'''

from phub import ( core, utils, consts, classes, parser, errors )

# Shortcuts
from phub.core import Client
from phub.classes import Video, User
from phub.utils import Quality, Category

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
    
    utils.log('PHUB', 'Switched logging to', bool(boolean), level = 6)

# EOF
