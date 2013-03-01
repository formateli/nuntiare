# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Link(object):
    def __init__(self, report, parent, obj=None):
        self.report=report  # Main Report() object
        self.parent=parent  # Parent element
        self.obj=obj        # object itself. It is used to assign parent to others

