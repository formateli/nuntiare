# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import logging
import os
from version import VERSION, get_version

__author__ = 'Fredy Ramirez'
__copyright__='(C) 2013-2014 Fredy Ramirez <http://www.pescaoylimon.com>'
__version__ = get_version()
__license__='GNU GENERAL PUBLIC LICENSE Version 3'
__directory__=os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('Nuntiare')

__reports__={} # Reports cache

