# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... report.style import StyleInfo
from ... report.report_items import ReportItemsInfo
from ... tools import get_element_from_parent

class HtmlRectangle(object):
    def __init__(self, report, definition):    
        self.type = "PageRectangle"
        self.name = None
        self.top = 0.0
        self.left = 0.0
        self.width = None
        self.height = definition.height
        self.parent = None
        self.style = StyleInfo(report, get_element_from_parent(definition, "Style"))
        self.items_info = ReportItemsInfo(report, definition, self)
        
    def get_item_list(self):
        result=[]
        if self.items_info:
            result = self.items_info.item_list
        return result        

