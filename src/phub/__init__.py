'''
## PHUB v4.7

See https://phub.readthedocs.io/en/latest/ for docs.
See https://github.com/EchterAlsFake/PHUB for code.
'''

# Package description
__author__ = 'Egsagon, EchterAlsFake'
__copyright__ = 'Copyright 2024, PHUB'
__license__ = 'GPLv3'
__version__  = '4.7.2'

__all__ = ['Client', 'core', 'utils',
           'consts', 'errors', 'objects', 'modules']

# Shortcuts
from .core import Client

# Sub modules
from . import core
from . import utils
from . import consts
from . import errors

# Sub packages
from . import objects
from . import modules

# Sub packages content
from .objects import *
from .modules import *

# EOF
