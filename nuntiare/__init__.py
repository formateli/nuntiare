# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import logging
import os
from decimal import Decimal
from ConfigParser import ConfigParser
from version import VERSION, get_version

__author__ = 'Fredy Ramirez'
__copyright__='(C) 2013-2014 Fredy Ramirez <http://www.pescaoylimon.com>'
__version__ = get_version()
__license__='GNU GENERAL PUBLIC LICENSE Version 3'
__directory__=os.path.dirname(os.path.realpath(__file__))

cfg = os.path.join(__directory__, "nuntiare.cfg")
__config__ = ConfigParser()
__config__.read(cfg)

if not __config__.has_option('general', 'pixels_per_inch'):
    __pixels_per_inch__ = Decimal(72) # use the standard 72dpi
__pixels_per_inch__ = Decimal(__config__.get('general', 'pixels_per_inch')) # TODO--> should be a function

logger = logging.getLogger('Nuntiare')

__reports__={} # Reports cache

