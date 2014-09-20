# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from section import HeaderInfo, FooterInfo, BodyInfo
from report_items import ReportItemsInfo
from .. tools import get_expression_value_or_default, inch_2_mm

class Pages(object):
    def __init__(self, report):
        self.report = report                        
        page_def = report.report_def.get_element('Page')

        self.height = get_expression_value_or_default(report, page_def, "PageHeight", inch_2_mm(11))
        self.width = get_expression_value_or_default(report, page_def, "PageWidth", inch_2_mm(8.5))
        if self.height <= 0:
            raise_error_with_log("Report 'PageHeight' must be greater than 0.")
        if self.width <= 0:
           raise_error_with_log("Report 'PageWidth' must be greater than 0.")

        self.margin_top = get_expression_value_or_default(report, page_def, "TopMargin", 0.0)
        self.margin_left = get_expression_value_or_default(report, page_def, "LeftMargin", 0.0)
        self.margin_right = get_expression_value_or_default(report, page_def, "RightMargin", 0.0)
        self.margin_bottom = get_expression_value_or_default(report, page_def, "BottomMargin", 0.0)

        self.columns = get_expression_value_or_default(report, page_def, "Columns", 1)
        self.column_spacing = get_expression_value_or_default(report, page_def, "ColumnSpacing", inch_2_mm(0.5))

        self.available_width = self.width - self.margin_left - self.margin_right
        self.available_height = self.height - self.margin_top - self.margin_bottom
        
        self.header = self.get_header_footer(page_def, "PageHeader")
        self.footer = self.get_header_footer(page_def, "PageFooter")
        self.body = BodyInfo(report, report.report_def.get_element("Body"))

        if self.body.height == 0 or self.body.height > self.available_height:
            self.body.height = self.available_height
        if self.body.height < self.available_height:
            self.available_height = self.body.height

        self.body_items = ReportItemsInfo(report, self.body.definition, None)

    def get_header_footer(self, page_def, element_name):
        if page_def:
            el_def = page_def.get_element(element_name)
            if el_def:
                if element_name == 'PageHeader':
                    return HeaderInfo(self.report, el_def) 
                else:
                    return FooterInfo(self.report, el_def)

