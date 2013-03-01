# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ConfigParser import ConfigParser
import os
import sys
from nuntiare import __directory__

def get_render(render_name):
    '''
    Return a render API module with alias render_name
    '''

    cfg = os.path.join(__directory__, "nuntiare.cfg")

    config = ConfigParser()
    config.read(cfg)

    if not config.has_option('renders', render_name):
        return None
    module = config.get('renders', render_name)
    render = __import__(module, fromlist = ["*"])            

    return render
