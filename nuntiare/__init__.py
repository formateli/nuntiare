# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import sys
import os
import logging
from importlib import import_module
from . logger import NuntiareLog

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


PROJECT_NAME = 'Nuntiare'
AUTHOR = 'Fredy Ramirez'
COPYRIGHT = '2013-2018, Fredy Ramirez - http://www.formateli.com'
LICENSE = 'GNU GENERAL PUBLIC LICENSE V3'
VERSION = '0.1.0'
DIRECTORY = os.path.dirname(os.path.realpath(__file__))


sys.path.insert(0, os.path.dirname(DIRECTORY))

cfg = os.path.join(DIRECTORY, 'nuntiare.cfg')
CONFIG = ConfigParser()
CONFIG.read(cfg)


def get_config_value(section, option, default_value):
    result = None
    if CONFIG.has_option(section, option):
        result = CONFIG.get(section, option)
    else:
        result = default_value
    return result

__pixels_per_inch__ = float(
    get_config_value('general', 'pixels_per_inch', 72.0))

# Configure logging
LOGGER = NuntiareLog(get_config_value('logging', 'logger_level', 'DEBUG'))

log_file = get_config_value('logging', 'file', '')
if log_file != '':
    max_bytes = int(get_config_value('logging', 'size', 5)) * 1024
    count = int(get_config_value('logging', 'count', 5))
    file_level = get_config_value('logging', 'file_level', 'DEBUG')

    try:
        rotating_fh = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=count)
    except IOError:
        rotating_fh = None

    if rotating_fh:
        LOGGER.add_handler(
            rotating_fh,
            level=file_level,
            formatter='%(levelname)s: %(message)s')


# FontManager

LOGGER.debug('Loading Font Manager...')

fm = get_config_value('font', 'manager', 'nuntiare.font.FontManager')
i = fm.rindex('.')
module_name = fm[:i]
class_name = fm[i + 1:]
font_manager = import_module(module_name)
FontManager = getattr(font_manager, class_name)
if hasattr(FontManager, '_get_font_manager'):
    FontManager = FontManager._get_font_manager()
LOGGER.debug('  ' + FontManager.get_description())
