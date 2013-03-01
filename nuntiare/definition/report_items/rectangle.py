# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_item import ReportItem

class Rectangle(ReportItem):
    def __init__(self, node, lnk):
        super(Rectangle, self).__init__(node, lnk)
