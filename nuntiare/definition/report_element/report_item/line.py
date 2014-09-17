# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_item import ReportItem

class Line(ReportItem):
    '''
    The Line element has no additional attributes/elements beyond what it inherits from ReportItem
    Negative heights/widths allow for lines that are drawn up and/or left from their origin.
    Although negative Height and Width are allowed, both Top+Height and Left+Width must be
    nonnegative valid sizes.
    '''
    
    def __init__(self, node, lnk):
        super(Line, self).__init__("Line", node, lnk, None)
        
