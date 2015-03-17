# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . style import StyleInfo
from .. definition.expression import Expression

''' 
    Page sections info: Header, Footer and Body
'''

class SectionInfo(object):
    def __init__(self, report, definition):
        self.definition = definition 
        self.height = Expression.get_value_or_default(report,definition,"Height", 0.0)
        self.style = None
        if definition:
            style_def = definition.get_element("Style")
            if style_def:
                self.style = StyleInfo(report, style_def)


class HeaderFooterInfo(SectionInfo):
    def __init__(self, report, definition):
        super(HeaderFooterInfo, self).__init__(report, definition)
        self.print_on_first_page = definition.print_on_first_page
        self.print_on_last_page = definition.print_on_last_page


class HeaderInfo(HeaderFooterInfo):
    def __init__(self, report, definition):
        super(HeaderInfo, self).__init__(report, definition)


class FooterInfo(HeaderFooterInfo):
    def __init__(self, report, definition):
        super(FooterInfo, self).__init__(report, definition)


class BodyInfo(SectionInfo):
    def __init__(self, report, definition):
        super(BodyInfo, self).__init__(report, definition)

