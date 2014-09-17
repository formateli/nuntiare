# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

#from section import HeaderInfo, FooterInfo, BodyInfo
#from get_report_items import ReportItemsInfo
#from ..tools import get_expression_value_or_default, inch_2_mm

class Pages(object):
    def __init__(self, report):
        self.report = report
#        self.page_height = get_expression_value_or_default(report.definition, "PageHeight", inch_2_mm(11))
#        self.page_width = get_expression_value_or_default(report.definition, "PageWidth", inch_2_mm(8.5))

#        if self.page_height <= 0:
#            raise_error_with_log("Report 'PageHeight' must be greater than 0.")
#        if self.page_width <= 0:
#           raise_error_with_log("Report 'PageWidth' must be greater than 0.")

#        self.page_margin_top = get_expression_value_or_default(report.definition, "TopMargin", 0)
#        self.page_margin_left = get_expression_value_or_default(report.definition, "LeftMargin", 0)
#        self.page_margin_right = get_expression_value_or_default(report.definition, "RightMargin", 0)
#        self.page_margin_bottom = get_expression_value_or_default(report.definition, "BottomMargin", 0)

#        self.available_width = self.page_width - self.page_margin_left - self.page_margin_right
#        self.available_height = self.page_height - self.page_margin_top - self.page_margin_bottom
        
#        self.header = HeaderInfo(report.definition.get_element("PageHeader"))
#        self.footer = FooterInfo(report.definition.get_element("PageFooter"))
#        self.body = BodyInfo(report.definition.get_element("Body"))

#        if self.body.height == 0 or self.body.height > self.available_height:
#            self.body.height = self.available_height
#        if self.body.height < self.available_height:
#            self.available_height = self.body.height

#        self.body_items = ReportItemsInfo(self.body.definition, None)

