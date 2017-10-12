# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . outcome.page_item import PageItemsInfo
from . import LOGGER


class Result(object):
    def __init__(self, report):
        self.report = report
        self.page_def = report.definition.Page

        self.height = self.page_def.PageHeight
        self.width = self.page_def.PageWidth

        if self.height <= 0:
            LOGGER.error(
                "Report 'PageHeight' must be greater than 0.", True)
        if self.width <= 0:
            LOGGER.error(
                "Report 'PageWidth' must be greater than 0.", True)

        self.margin_top = self.page_def.TopMargin
        self.margin_left = self.page_def.LeftMargin
        self.margin_right = self.page_def.RightMargin
        self.margin_bottom = self.page_def.BottomMargin

        self.header = None
        self.footer = None
        if self.page_def.PageHeader:
            self.header = HeaderFooterInfo(
                report, self.page_def.PageHeader)
        if self.page_def.PageFooter:
            self.footer = HeaderFooterInfo(
                report, self.page_def.PageFooter)

        self.body = BodyInfo(report, report.definition.Body)
        self.body.set_available_height(
            self.height, self.margin_top, self.margin_bottom,
            self.header, self.footer)

        self.available_width = \
            self.width - self.margin_left - self.margin_right

        self.columns = self.page_def.Columns
        self.column_spacing = self.page_def.ColumnSpacing
        self.style = report.get_style(self.page_def)
        self.body.run_items()


class _SectionInfo(object):
    def __init__(self, report, definition, has_height):
        self.report = report
        self.definition = definition
        self.available_height = 0.0

        if has_height:
            self.height = definition.Height
            self.available_height = self.height

        self.items = None
        self.style = report.get_style(definition)

    def run_items(self):
        self.items = None
        self.items = PageItemsInfo(
            self.report, self.definition, parent=None)


class HeaderFooterInfo(_SectionInfo):
    def __init__(self, report, definition):
        super(HeaderFooterInfo, self).__init__(report, definition, True)
        self.print_on_first_page = definition.PrintOnFirstPage
        self.print_on_last_page = definition.PrintOnLastPage


class BodyInfo(_SectionInfo):
    def __init__(self, report, definition):
        super(BodyInfo, self).__init__(report, definition, False)

    def set_available_height(
            self, page_height,
            margin_top, margin_bottom,
            header, footer):
        self.available_height = \
            page_height - margin_top - margin_bottom
        if header:
            self.available_height -= header.height
        if footer:
            self.available_height -= footer.height
