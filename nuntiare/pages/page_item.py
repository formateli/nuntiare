# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import cairo
import pango
import pangocairo
from style import StyleInfo
from decimal import Decimal
from ..tools import raise_error_with_log, get_element_from_parent, \
    get_expression_value_or_default, get_size_in_unit, dot_2_mm, point_2_mm
from get_report_items import get_report_items

class PageItem(object):
    def __init__(self, type, report_item_def):
        self.type=type
        self.parent=None
        self.item_list=[]
        self.name=get_expression_value_or_default(report_item_def, "Name", "")
        self.report_item_def = report_item_def
        self.top = get_expression_value_or_default(report_item_def, "Top", 0)
        self.left = get_expression_value_or_default(report_item_def, "Left", 0)
        self.height = get_expression_value_or_default(report_item_def, "Height", 0)
        self.width = get_expression_value_or_default(report_item_def, "Width", 0)        
        self.style = StyleInfo(get_element_from_parent(report_item_def, "Style"))


class PageLine(PageItem):
    def __init__(self, report_item_def):
        super(PageLine, self).__init__("PageLine", report_item_def)


class PageRectangle(PageItem):
    def __init__(self, report_item_def):
        super(PageRectangle, self).__init__("PageRectangle", report_item_def)
        self.item_list=get_report_items(report_item_def, self)


class PageText(PageItem):
    def __init__(self, report_item_def):
        super(PageText, self).__init__("PageText", report_item_def)
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

