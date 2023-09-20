'''
PHUB v4.0.0

See github.com/Egsagon/PHUB for docs.
'''

__all__ = ['Client', 'Quality', 'core', 'utils', 'consts', 'errors']

# Shortcuts
from .core import Client
from .locals import Quality

from . import core
from . import utils
from . import consts
from . import errors

from .objects import *
from .modules import *

# why
# import logging
# logging.getLogger('phub').addHandler(logging.NullHandler())

# EOF