'''
Initialises the PHUB package.
'''

from phub import ( core, utils, consts, classes, parser)

# Shortcuts
from phub.core import Client
from phub.consts import Quality
from phub.classes import Video, User

# Debugging controls
from sys import stdout
from io import TextIOBase

def debug(boolean: bool, file: TextIOBase = stdout) -> None:
    '''
    Whether to log everything to stdout.
    
    Arguments
        boolean: Value to set debug to.
        file (optional): File to output logs to.
    '''
    
    utils.DEBUG = boolean
    utils.DEBUG_FILE = file
    
    utils.log('init_', 'Switching logging to', boolean)


# TODO - Handle user with * channels
# TODO - Video iterator for User object

# EOF