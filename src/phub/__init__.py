'''
## PHUB v4.4

See https://phub.readthedocs.io/en/latest/ for docs.
See https://github.com/EchterAlsFake/PHUB for code.
'''

# Package description
__author__ = 'Egsagon, EchterAlsFake'
__copyright__ = 'Copyright 2024, PHUB'
__license__ = 'GPLv3'
__version__  = '4.4'

__all__ = ['Client', 'Quality', 'core', 'utils',
           'consts', 'errors', 'objects', 'modules']

# Shortcuts
from .core import Client
from .utils import Quality

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
