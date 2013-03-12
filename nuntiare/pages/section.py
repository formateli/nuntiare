# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.tools import raise_error_with_log, get_element_value_or_default, inch_2_mm


''' 
    Page sections info: Header, Footer and Body
'''

class SectionInfo(object):
    def __init__(self, element):
        self.definition = element 
        self.height = 0
        self.style = None
        if element:
            self.height = get_element_value_or_default(element.get_element("Height"), 0)
            self.style = get_element_value_or_default(element.get_element("Style"), None)


class HeaderFooterInfo(SectionInfo):
    def __init__(self, element):
        super(HeaderFooterInfo, self).__init__(element)
        self.print_on_first_page = False
        self.print_on_last_page = False
        if element:
            self.height = get_element_value_or_default(element.get_element("Height"), 0)
            self.print_on_first_page = get_element_value_or_default(element.get_element("PrintOnFirstPage"), False)
            self.print_on_last_page = get_element_value_or_default(element.get_element("PrintOnLastPage"), False)


class HeaderInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(HeaderInfo, self).__init__(element)


class FooterInfo(HeaderFooterInfo):
    def __init__(self, element):
        super(FooterInfo, self).__init__(element)


class BodyInfo(SectionInfo):
    def __init__(self, element):
        if not element:
            raise_error_with_log("Body section is requiered!")
        super(BodyInfo, self).__init__(element)
        self.columns = get_element_value_or_default(element.get_element("Columns"), 1)
        self.column_spacing = get_element_value_or_default(element.get_element("ColumnSpacing"), inch_2_mm(0.5))


