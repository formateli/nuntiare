# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from types.element import Element
from .. tools import get_expression_value_or_default, inch_2_mm

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
        
        self.height = get_expression_value_or_default(None, self, "PageHeight", inch_2_mm(11))
        self.width = get_expression_value_or_default(None, self, "PageWidth", inch_2_mm(8.5))

        if self.height <= 0:
            raise_error_with_log("Report 'PageHeight' must be greater than 0.")
        if self.width <= 0:
           raise_error_with_log("Report 'PageWidth' must be greater than 0.")
           
        self.margin_top = get_expression_value_or_default(None, self, "TopMargin", 0.0)
        self.margin_left = get_expression_value_or_default(None, self, "LeftMargin", 0.0)
        self.margin_right = get_expression_value_or_default(None, self, "RightMargin", 0.0)
        self.margin_bottom = get_expression_value_or_default(None, self, "BottomMargin", 0.0)
        
        self.columns = get_expression_value_or_default(None, self, "Columns", 1)
        self.column_spacing = get_expression_value_or_default(None, self, "ColumnSpacing", inch_2_mm(0.5))
        
