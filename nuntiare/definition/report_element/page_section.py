# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_element import ReportElement
from .. types.element import Element
from ... tools import get_expression_value_or_default

class PageSection(ReportElement):
    '''
    The virtual PageSection element defines the layout of report items to appear at the top or bottom
    of every page of the report. The PageSection element itself is not used. Only subtypes of
    PageSection are used: PageHeader, PageFooter. It inherits from ReportElement.
    '''

    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'Height': [Element.SIZE, True], 
                  'PrintOnFirstPage': [Element.BOOLEAN, True],
                  'PrintOnLastPage': [Element.BOOLEAN, True],
                 }
        super(PageSection, self).__init__(node, elements, lnk)
        self.height = get_expression_value_or_default(None, self, "Height", 0.0)
        self.print_on_first_page = get_expression_value_or_default(None, self, "PrintOnFirstPage", True)
        self.print_on_last_page = get_expression_value_or_default(None, self, "PrintOnLastPage", True)
                

class PageHeader(PageSection):
    '''
    The PageHeader element defines the layout of report items to appear at the top of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)


class PageFooter(PageSection):
    '''
    The PageFooter element defines the layout of report items to appear at the bottom of every page of
    the report. It has no properties beyond those it inherits from PageSection.
    '''
    
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)

