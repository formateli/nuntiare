# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from style import StyleInfo
from get_report_items import ReportItemsInfo
from ..tools import get_element_from_parent, get_expression_value_or_default

class PageItem(object):
    def __init__(self, type, report_item_def, parent):
        self.type=type # Type of PageItem: PageBreak, PageLine. PageRectangle, PageText, PageGrid 
        self.parent=parent
        self.items_info=None # Only for thoose that can content 'ReportItems' 
        self.report_item_def = report_item_def
        self.name=get_expression_value_or_default(report_item_def, "Name", "")
        self.top = get_expression_value_or_default(report_item_def, "Top", 0)
        self.left = get_expression_value_or_default(report_item_def, "Left", 0)
        self.height = get_expression_value_or_default(report_item_def, "Height", 0)
        self.width = get_expression_value_or_default(report_item_def, "Width", 0)        
        self.style = StyleInfo(get_element_from_parent(report_item_def, "Style"))

        if parent:
            if parent.height > 0 and self.height == 0:
                self.height = parent.height - parent.top
            if parent.width > 0 and self.width == 0:
                self.width = parent.width - parent.left

    def get_item_list(self):
        result=[]
        if self.items_info:
            result = self.items_info.item_list
        return result


class PageBreak(PageItem):
    def __init__(self):
        super(PageBreak, self).__init__("PageBreak", None, None)


class PageLine(PageItem):
    def __init__(self, report_item_def, parent):
        super(PageLine, self).__init__("PageLine", report_item_def, parent)


class PageRectangle(PageItem):
    def __init__(self, report_item_def, parent):
        super(PageRectangle, self).__init__("PageRectangle", report_item_def, parent)
        self.page_break_at_start = get_expression_value_or_default(report_item_def, "PageBreakAtStart", False)
        self.page_break_at_end = get_expression_value_or_default(report_item_def, "PageBreakAtEnd", False)
        self.items_info = ReportItemsInfo(report_item_def, self)


class PageText(PageItem):
    def __init__(self, report_item_def, parent):
        super(PageText, self).__init__("PageText", report_item_def, parent)
        self.value = get_expression_value_or_default(report_item_def, "Value", None)
        self.value_formatted = None 
        if self.value != None:
            if self.style.text.format:
                self.value_formatted = self.style.text.format.format(self.value)
            else:
                self.value_formatted = str(self.value)
            self.value = str(self.value)
        self.can_grow = get_expression_value_or_default(report_item_def, "CanGrow", False)
        self.can_shrink = get_expression_value_or_default(report_item_def, "CanShrink", False)

