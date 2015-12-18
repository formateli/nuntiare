# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
from .. import logger
from .. data import DataType

class PageItemsInfo():
    def __init__(self, report, definition, parent):
        self.item_list = []
        self.total_height = 0
        self.min_height = sys.float_info.max
        self.max_height = 0
        self.can_grow = False
        self.can_shrink = False

        items = []
        if definition and definition.ReportItems:
            items = definition.ReportItems.reportitems_list

        for it in items:
            page_item = PageItem.page_item_factory(report, it, parent)
            self.total_height = self.total_height + page_item.height 
            if page_item.height > self.max_height:
                self.max_height =  page_item.height
            if page_item.height < self.min_height:
                self.min_height =  page_item.height
            if page_item.type == "PageText":
                if page_item.can_grow:
                    self.can_grow = True
                if page_item.can_shrink:
                    self.can_shrink = True
            self.item_list.append(page_item)


class PageItem(object):
    def __init__(self, type_, report, 
                 report_item_def, parent):
        self.type = type_ # Type of PageItem: PageLine. PageRectangle, PageText, etc.
        self.report = report
        self.parent = parent
        self.items_info = None # Only for those that can content 'ReportItems'
        self.report_item_def = report_item_def
        self.name = report.get_value(
                report_item_def, "Name", None)
        self.top = report.get_value(
                report_item_def, "Top", 0.0)
        self.left = report.get_value(
                report_item_def, "Left", 0.0)
        self.height = report.get_value(
                report_item_def, "Height", 0.0)
        self.width = report.get_value(
                report_item_def, "Width", 0.0)
        self.style = report.get_style(report_item_def)

        if parent and type_ != "RowCell" and parent.type == "RowCell":
            self.height = 0
            self.width = 0
            self.left = 0
            self.top = 0
        self._normalize_height_width()

    def _normalize_height_width(self):
        if self.parent:
            if self.parent.height > 0 and self.height == 0:
                self.height = self.parent.height - self.parent.top
            if self.parent.width > 0 and self.width == 0:
                self.width = self.parent.width - self.parent.left

    def get_item_list(self):
        if self.items_info:
            return self.items_info.item_list

    @staticmethod
    def page_item_factory(report, it, parent):
        page_item = None
        if it.type == "Line":
            page_item = PageLine(report, it, parent)
        if it.type == "Rectangle":
            page_item = PageRectangle(report, it, parent)
        if it.type == "Textbox":
            page_item = PageText(report, it, parent)
        if it.type == "Tablix":
            from . page_tablix import PageTablix
            page_item = PageTablix(report, it, parent)

        if not page_item:
            logger.error(
                "Error trying to get Report item. Invalid definition element '{0}'".format(it), True)

        return page_item


class PageLine(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageLine, self).__init__("PageLine", report, report_item_def, parent)


class PageRectangle(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageRectangle, self).__init__("PageRectangle", report, report_item_def, parent)
        self.keep_together = report.get_value(
                report_item_def, "KeepTogether", True)
        self.omit_border_on_page_break = report.get_value(
                report_item_def, "OmitBorderOnPageBreak", True)
        self.page_break = report.get_value(
                report_item_def.get_element("PageBreak"), "BreakLocation", None)
        self.items_info = PageItemsInfo(report, report_item_def, self)


class PageText(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageText, self).__init__("PageText", report, report_item_def, parent)
        self.can_grow = report.get_value(
                report_item_def, "CanGrow", False)
        self.can_shrink = report.get_value(
                report_item_def, "CanShrink", False)
        self.hide_duplicates = report.get_value(
                report_item_def, "HideDuplicates", None)

        self.value = report.get_value(
                report_item_def, "Value", None)

        self.value_formatted = ""
        if self.value != None:
            if self.style.format:
                try:
                    self.value_formatted = DataType.get_value("String",
                            self.style.format.format(self.value))
                except Exception:
                    logger.warn(
                        "Invalid format operation. Value '{0}' - Format '{1}'. Ignored.".format(
                            self.value, self.style.format))
                    self.value_formatted = DataType.get_value("String", self.value)
            else:
                self.value_formatted = DataType.get_value("String", self.value)

