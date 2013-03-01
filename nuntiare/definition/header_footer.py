# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from element import Element

class PageHeaderFooter(Element):
    def __init__(self, node, lnk):
        elements={'Height': [Element.SIZE], 
                  'PrintOnFirstPage': [Element.BOOLEAN],
                  'PrintOnLastPage': [Element.BOOLEAN],
                  'Style': [Element.ELEMENT],
                  'ReportItems': [Element.ELEMENT],
                  'Style': [Element.ELEMENT],
                 }

        super(PageHeaderFooter, self).__init__(node, elements, lnk)

class PageHeader(PageHeaderFooter):
    def __init__(self, node, lnk):
        super(PageHeader, self).__init__(node, lnk)

class PageFooter(PageHeaderFooter):
    def __init__(self, node, lnk):
        super(PageFooter, self).__init__(node, lnk)




