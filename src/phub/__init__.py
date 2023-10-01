'''
PHUB v4.0

See https://github.com/Egsagon/PHUB for docs.
'''

# Shortcuts
from .core import Client
from .locals import Quality

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

# Avoid importing everything from subpackages
# when using star imports
__all__ = ['Client', 'Quality', 'core', 'utils',
           'consts', 'errors', 'objects', 'modules']

# EOF