# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from importlib import import_module
from .. import __config__

def get_render(render_name):
    '''
    Return a render API module with alias render_name
    '''

    if not __config__.has_option('renders', render_name):
        return None
    module = __config__.get('renders', render_name)
    render = import_module(module)
    return render.get_render_object()

