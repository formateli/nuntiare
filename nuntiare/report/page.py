# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from section import HeaderInfo, FooterInfo, BodyInfo
from report_items import ReportItemsInfo

class Pages(object):
    def __init__(self, report):
        self.report = report                
        
        page_def = report.report_def.get_element('Page')
        if not page_def:
            return

        self.available_width = page_def.width - page_def.margin_left - page_def.margin_right
        self.available_height = page_def.height - page_def.margin_top - page_def.margin_bottom
        
        self.header = HeaderInfo(report, page_def.get_element("PageHeader"))
        self.footer = FooterInfo(report, page_def.get_element("PageFooter"))
        self.body = BodyInfo(report, report.report_def.get_element("Body"))

        if self.body.height == 0 or self.body.height > self.available_height:
            self.body.height = self.available_height
        if self.body.height < self.available_height:
            self.available_height = self.body.height

        self.body_items = ReportItemsInfo(report, self.body.definition, None)

