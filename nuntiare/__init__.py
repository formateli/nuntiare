# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
import os
import logging
from . logger import NuntiareLog

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser # Python 3
    
from . version import VERSION, get_version

__author__ = 'Fredy Ramirez'
__copyright__='(C) 2013-2015 Fredy Ramirez <http://www.formateli.com>'
__version__ = get_version()
__license__ = 'GNU GENERAL PUBLIC LICENSE Version 3'
__directory__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, os.path.dirname(__directory__))

cfg = os.path.join(__directory__, "nuntiare.cfg")
__config__ = ConfigParser()
__config__.read(cfg)


def get_config_value(section, option, default_value):
    result=None 
    if __config__.has_option(section, option):
        result = __config__.get(section, option)
    else:
        result = default_value
    return result

__pixels_per_inch__ = float(get_config_value('general', 'pixels_per_inch', 72.0))

# Configure logging

logger = NuntiareLog(get_config_value('logging', 'logger_level', 'DEBUG'))

log_file = get_config_value('logging', 'file', '')
if log_file != '':
    max_bytes = int(get_config_value('logging', 'size', 5)) * 1024
    count = int(get_config_value('logging', 'count', 5))
    file_level = get_config_value('logging', 'file_level', 'DEBUG')

    try:    
        rotating_fh=logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=count)
    except IOError:
        rotating_fh=None
        
    if rotating_fh:
        logger.add_handler(rotating_fh, level=file_level, 
                formatter='%(levelname)s: %(message)s')

