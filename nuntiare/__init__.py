# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
import os
import logging
import logging.handlers
from ConfigParser import ConfigParser
from version import VERSION, get_version

__author__ = 'Fredy Ramirez'
__copyright__='(C) 2013-2014 Fredy Ramirez <http://www.pescaoylimon.com>'
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

def get_level_from_string(level):
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL

def add_logger_handler(handler, level=None, formatter=None):
    if level:
        handler.setLevel(level)
    if formatter:
        handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)

__pixels_per_inch__ = float(get_config_value('general', 'pixels_per_inch', 72.0))

# Configure logging
logger = logging.getLogger('Nuntiare')
logger.setLevel(get_level_from_string(get_config_value('logging', 'logger_level', 'DEBUG')))

add_logger_handler(logging.NullHandler())

log_file = get_config_value('logging', 'file', '')
if log_file != '':
    max_bytes = int(get_config_value('logging', 'size', 1024))
    count = int(get_config_value('logging', 'count', 5))
    file_level = get_level_from_string(get_config_value('logging', 'file_level', 'DEBUG'))
    add_logger_handler(logging.handlers.RotatingFileHandler(
              log_file, maxBytes=max_bytes, backupCount=count), 
              level=file_level, 
              formatter='%(levelname)s: %(message)s')

stdout_level = get_level_from_string(get_config_value('logging', 'stdout_level', None))
if stdout_level:
    add_logger_handler(logging.StreamHandler(sys.stdout), stdout_level)
    
