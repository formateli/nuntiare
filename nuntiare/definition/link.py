# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Link(object):
    def __init__(self, report_def, parent, obj=None):
        self.report_def=report_def  # Main ReportDef() object
        self.parent=parent          # Parent element
        self.obj=obj                # object itself. It is used to assign parent to others

