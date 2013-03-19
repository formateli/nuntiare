# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from style import StyleInfo
from nuntiare.tools import get_element_from_parent

class PageItem(object):
    def __init__(self, report_item, parent_top, parent_left):
        self.report_item = report_item
        self.top = report_item.get_element("Top").value() + parent_top
        self.left = report_item.get_element("Left").value() + parent_left
        self.height = report_item.get_element("Height").value()
        self.width = report_item.get_element("Width").value()
        self.style = StyleInfo(get_element_from_parent(report_item, "Style"))


class PageLine(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageLine, self).__init__(report_item, parent_top, parent_left)


class PageRectangle(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageRectangle, self).__init__(report_item, parent_top, parent_left)


class PageText(PageItem):
    def __init__(self, report_item, parent_top, parent_left):
        super(PageText, self).__init__(report_item, parent_top, parent_left)
        v = report_item.get_element("Value")        
        self.value = None
        if v:
            self.value = v.value()

 
