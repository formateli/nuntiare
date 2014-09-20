# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from types.element import Element

class Page(Element):
    '''
    The Page element contains page layout information for the report.
    '''

    def __init__(self, node, lnk):
        elements={'PageHeader': [Element.ELEMENT],
                  'PageFooter': [Element.ELEMENT],
                  'PageHeight': [Element.SIZE, True],
                  'PageWidth': [Element.SIZE, True],
                  'InteractiveHeight': [Element.SIZE, True],
                  'InteractiveWidth': [Element.SIZE, True],
                  'LeftMargin': [Element.SIZE, True],
                  'RightMargin': [Element.SIZE, True],
                  'TopMargin': [Element.SIZE, True],
                  'BottomMargin': [Element.SIZE, True],
                  'Columns': [Element.INTEGER, True],
                  'ColumnSpacing': [Element.SIZE, True],
                  'Style': [Element.ELEMENT],                  
                 }
        super(Page, self).__init__(node, elements, lnk)
        
