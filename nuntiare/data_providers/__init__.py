# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ConfigParser import ConfigParser
import os
import sys
from nuntiare import __directory__

def get_data_provider(provider_name):
    "Returns an API 2.0 module for the dataprovider name especified in ../nuntiare.cfg"

    cfg = os.path.join(__directory__, "nuntiare.cfg")

    config = ConfigParser()
    config.read(cfg)

    if not config.has_option('data_providers', provider_name):
        return None
    module = config.get('data_providers', provider_name)
    provider = __import__(module, fromlist = ["*"])            

    return provider



