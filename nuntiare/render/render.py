# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
from importlib import import_module
from .. import __config__, logger

class Render(object):
    def __init__(self, extension=None):
        self.extension=extension 
        self.result_file=None

    def render(self, report, overwrite=True):
        if not report.page:
            logger.critical("No Page object in report. Have you executed run() in report object?", True)
            
        if self.extension:
            self.result_file = os.path.join(report.globals['output_directory'],
                report.globals['output_name'] + "." + self.extension)
            if not overwrite:
                if os.path.isfile(self.result_file):
                    logger.error("File '{0}' already exists.".format(self.result_file),
                        True, "IOError")

    def help(self):
        return "No help!"
        
    @staticmethod
    def get_render(render_name):
        '''
        Returns a derived Render object that corresponds to 'render_name'. Ex: html
        '''
        if not __config__.has_option('renders', render_name):
            return None
        module = __config__.get('renders', render_name)
        render = import_module(module)
        return render.get_render_object()

