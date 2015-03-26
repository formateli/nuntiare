# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . page_item.page_item import PageItemsInfo
from .. template.expression import Expression, Size
from .. import logger

class Page(object):
    def __init__(self, report):
        self.report = report
        self.page_def = report.parser.object.get_element('Page')
                
        self.height = report.parser.get_value(report, self.page_def,
            "PageHeight", Size.convert("in", "mm", 11))
        self.width = report.parser.get_value(report, self.page_def,
            "PageWidth", Size.convert("in", "mm", 8.5))

        if self.height <= 0:
            logger.error("Report 'PageHeight' must be greater than 0.", True)
        if self.width <= 0:
            logger.error("Report 'PageWidth' must be greater than 0.", True)

        self.margin_top = report.parser.get_value(report,self.page_def,"TopMargin", 0.0)
        self.margin_left = report.parser.get_value(report,self.page_def,"LeftMargin", 0.0)
        self.margin_right = report.parser.get_value(report,self.page_def,"RightMargin", 0.0)
        self.margin_bottom = report.parser.get_value(report,self.page_def,"BottomMargin", 0.0)

        self.columns = report.parser.get_value(report,self.page_def,"Columns", 1)
        self.column_spacing = report.parser.get_value(report,self.page_def,
            "ColumnSpacing", Size.convert("in", "mm", 0.5))

        self.available_width = self.width - self.margin_left - self.margin_right
        self.available_height = self.height - self.margin_top - self.margin_bottom
        
        self.style = report.style.get_style_info(self.page_def.get_element("Style")) 
        
        self.header = self.get_header_footer(self.page_def, "PageHeader")
        self.footer = self.get_header_footer(self.page_def, "PageFooter")
        self.body = BodyInfo(report, report.parser.object.get_element("Body"))

        if self.body.height == 0 or self.body.height > self.available_height:
            self.body.height = self.available_height
        if self.body.height < self.available_height:
            self.available_height = self.body.height

        self.body.get_items()

    def get_header_footer(self, page_def, element_name):
        if page_def:
            el_def = page_def.get_element(element_name)
            if el_def:
                if element_name == 'PageHeader':
                    return HeaderInfo(self.report, el_def) 
                else:
                    return FooterInfo(self.report, el_def)


class _SectionInfo(object):
    def __init__(self, report, definition):
        self.report = report
        self.definition = definition 
        self.height = Expression.get_value_or_default(
                report, definition, "Height", 0.0)
        self.style = None
        self.items = None
        if definition:
            if definition.has_element("Style"):
                self.style = report.style.get_style_info(
                        definition.get_element("Style")
                    )
    def get_items(self):
        self.items = PageItemsInfo(
            self.report, self.definition, parent=None)
        return self.items


class _HeaderFooterInfo(_SectionInfo):
    def __init__(self, report, definition):
        super(_HeaderFooterInfo, self).__init__(report, definition)
        self.print_on_first_page = Expression.get_value_or_default(
                report, definition, "PrintOnFirstPage", True
            )
        self.print_on_last_page = Expression.get_value_or_default(
                report, definition, "PrintOnLastPage", True
            )


class HeaderInfo(_HeaderFooterInfo):
    def __init__(self, report, definition):
        super(HeaderInfo, self).__init__(report, definition)


class FooterInfo(_HeaderFooterInfo):
    def __init__(self, report, definition):
        super(FooterInfo, self).__init__(report, definition)


class BodyInfo(_SectionInfo):
    def __init__(self, report, definition):
        super(BodyInfo, self).__init__(report, definition)

