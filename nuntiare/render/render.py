# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os

class Render(object):
    def __init__(self, extension=None):
        self.extension=extension 
        self.result_file=None

    def render(self, report):
        if self.extension:
            self.result_file = os.path.join(report.output_directory, 
                report.output_name + "." + self.extension)

    def help(self):
        return "No help!"

