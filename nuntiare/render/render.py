# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from importlib import import_module
from .. import __config__

class Render(object):
    def __init__(self, extension=None):
        self.extension=extension 
        self.result_file=None

    def render(self, report):
        if self.extension:
            self.result_file = os.path.join(report.report_def.output_directory, 
                report.report_def.output_name + "." + self.extension)

    def help(self):
        return "No help!"
        
    @staticmethod
    def get_render(render_name):       
        '''
        Returns a derived Render object that corresponds to render_name. Ex: html
        '''
        if not __config__.has_option('renders', render_name):
            return None
        module = __config__.get('renders', render_name)
        render = import_module(module)
        return render.get_render_object()

