# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from style import StyleInfo
from ..tools import raise_error_with_log, get_expression_value_or_default, get_element_from_parent, inch_2_mm

''' 
    Page sections info: Header, Footer and Body
'''

class SectionInfo(object):
    def __init__(self, element):
        self.definition = element 
        self.height = get_expression_value_or_default(element, "Height", 0)
        self.style = None
        if element:
            self.style = StyleInfo(get_element_from_parent(element, "Style"))


class HeaderFooterInfo(SectionInfo):
    def __init__(self, element):
        super(HeaderFooterInfo, self).__init__(element)
        self.print_on_first_page = get_expression_value_or_default(element, "PrintOnFirstPage", False)
        self.print_on_first_page = get_expression_value_or_default(element, "PrintOnLastPage", False)


class HeaderInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(HeaderInfo, self).__init__(element)


class FooterInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(FooterInfo, self).__init__(element)


class BodyInfo(SectionInfo):
    def __init__(self, element):
        super(BodyInfo, self).__init__(element)
        self.columns = get_expression_value_or_default(element, "Columns", 1)
        self.column_spacing = get_expression_value_or_default(element, "ColumnSpacing", inch_2_mm(0.5))

