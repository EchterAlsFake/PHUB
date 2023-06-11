'''
Initialises the PHUB package.
'''

from phub import (
    core,
    utils,
    consts,
    classes,
    parser
)

# Shortcuts
from phub.core import Client
from phub.consts import Quality
from phub.classes import Video, User

# Debugging controls
import sys
from io import TextIOBase

def debug(boolean: bool, file: TextIOBase = sys.stdout) -> None:
    '''
    Whether to log everything to stdout.
    '''
    
    utils.DEBUG = boolean
    utils.DEBUG_FILE = file
    
    utils.log('init_', 'Switching logging to', boolean)


# TODO - Docstrings
# TODO - error args for assertions
# TODO - Handle user with * channels
# TODO - Video iterator for User object

# EOF