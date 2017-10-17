# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import sys
import cairo
from .. nuntiarepango import pango, NuntiarePango
from .. import LOGGER
from .. data.data_type import DataType


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
                self.max_height = page_item.height
            if page_item.height < self.min_height:
                self.min_height = page_item.height
            if page_item.type == 'PageText':
                if page_item.can_grow:
                    self.can_grow = True
                if page_item.can_shrink:
                    self.can_shrink = True
            self.item_list.append(page_item)

        # accomodates items according to
        # each new size (if any)
        for it in self.item_list:
            if it.height > it.original_height or \
                    it.width > it.original_width:
                self._accomodate(it)

    def _accomodate(self, it_ref):
        for it in self.item_list:
            if it == it_ref:
                continue
            gap = it_ref.in_zone_down(it_ref, it)
            if gap is not None:
                it.top = it_ref.top + it_ref.height + gap

            gap = it_ref.in_zone_left(it_ref, it)
            if gap is not None:
                it.left = it_ref.left + it_ref.width + gap


class PageItem(object):
    def __init__(self, type_, report,
                 report_item_def, parent):
        # Type of PageItem: PageLine. PageRectangle, PageText, etc.
        self.type = type_
        self.report = report
        self.parent = parent
        # Only for those that can content 'ReportItems'
        self.items_info = None
        self.report_item_def = report_item_def
        self.name = report.get_value(
            report_item_def, 'Name', None)
        self.top = report.get_value(
            report_item_def, 'Top', 0)
        self.left = report.get_value(
            report_item_def, 'Left', 0)
        self.zindex = report.get_value(
            report_item_def, 'ZIndex', -1)
        self.height = report.get_value(
            report_item_def, 'Height', 0)
        self.width = report.get_value(
            report_item_def, 'Width', 0)
        self.tool_tip = report.get_value(
            report_item_def, 'ToolTip', None)
        self.bookmark = report.get_value(
            report_item_def, 'Bookmark', None)
        self.repeat_with = report.get_value(
            report_item_def, 'RepeatWith', None)
        self.data_element_name = report.get_value(
            report_item_def, 'DataElementName', None)
        self.data_element_output = report.get_value(
            report_item_def, 'DataElementOutput', 'Auto')
        # TODO  Visibility, ActionInfo
        self.style = report.get_style(report_item_def, type_)

        if parent and type_ != 'RowCell' and parent.type == 'RowCell':
            self.height = 0.0
            self.width = 0.0
            self.left = 0.0
            self.top = 0.0
        self._normalize_height_width()

        self.original_top = self.top
        self.original_left = self.left
        self.original_height = self.height
        self.original_width = self.width

    @staticmethod
    def in_zone_down_x(it_ref, it_to_move):
        if it_to_move.original_top <= \
                (it_ref.original_top + it_ref.original_height):
            return
        if (it_to_move.original_left + it_to_move.original_width) <= \
                it_ref.original_left:
            return
        if it_to_move.original_left >= \
                (it_ref.original_left + it_ref.original_width):
            return

        return True

    @staticmethod
    def in_zone_down(it_ref, it_to_move):
        if it_to_move.original_top <= it_ref.original_top:
            return

        min_gap = it_to_move.original_top - \
            (it_ref.original_top + it_ref.original_height)

        if it_to_move.top >= (it_ref.top + it_ref.height + min_gap):
            return
        if it_to_move.left > (it_ref.left + it_ref.width):
            return
        if (it_to_move.left + it_to_move.width) < it_ref.left:
            return
        return min_gap

    @staticmethod
    def in_zone_right(it_ref, it_to_move):
        if it_to_move.original_left <= \
                (it_ref.original_left + it_ref.original_width):
            return
        if (it_to_move.original_top + it_to_move.original_height) <= \
                it_ref.original_top:
            return
        if it_to_move.original_top >= \
                (it_ref.original_top + it_ref.original_height):
            return
        return True

    @staticmethod
    def in_zone_left(it_ref, it_to_move):
        if it_to_move.original_left <= it_ref.original_left:
            return

        min_gap = it_to_move.original_left - \
            (it_ref.original_left + it_ref.original_width)

        if it_to_move.left >= (it_ref.left + it_ref.width + min_gap):
            return
        if it_to_move.top > (it_ref.top + it_ref.height):
            return
        if (it_to_move.top + it_to_move.height) < it_ref.top:
            return
        return min_gap

    def set_new_height(self, height):
        self.height = height
        if self.parent is not None and self.parent.type == 'RowCell':
            self.parent.set_new_height(height)

    def set_new_widht(self, height):
        self.width = width

    def _normalize_height_width(self):
        if self.parent:
            if self.parent.height > 0.0 and self.height == 0.0:
                self.height = self.parent.height - self.parent.top
            if self.parent.width > 0.0 and self.width == 0.0:
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
            err_msg = "Error trying to get Report item. " \
                "Invalid definition element '{0}'"
            logger.error(err_msg.format(it), True)

        return page_item


class PageLine(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageLine, self).__init__(
            'PageLine', report, report_item_def, parent)


class PageRectangle(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageRectangle, self).__init__(
            'PageRectangle', report, report_item_def, parent)
        self.omit_border_on_page_break = report.get_value(
            report_item_def, 'OmitBorderOnPageBreak', True)
        self.page_break = report.get_value(
            report_item_def.get_element('PageBreak'), 'BreakLocation', None)
        self.keep_together = report.get_value(
            report_item_def, 'KeepTogether', False)
        self.items_info = PageItemsInfo(report, report_item_def, self)


class PageText(PageItem):
    def __init__(self, report, report_item_def, parent):
        super(PageText, self).__init__(
            'PageText', report, report_item_def, parent)

        self.can_grow = report.get_value(
            report_item_def, 'CanGrow', False)
        self.can_shrink = report.get_value(
            report_item_def, 'CanShrink', False)
        self.hide_duplicates = report.get_value(
            report_item_def, 'HideDuplicates', None)
        self.keep_together = report.get_value(
            report_item_def, 'KeepTogether', False)
        self.data_element_style = report.get_value(
            report_item_def, 'DataElementStyle', 'Auto')
        # TODO ToggleImage

        self.value = report.get_value(
                report_item_def, 'Value', None)

        self.value_formatted = ''
        if self.value is not None:
            if self.style.format:
                try:
                    self.value_formatted = DataType.get_value(
                        'String', self.style.format.format(
                            self.value))
                except Exception:
                    err_msg = "Invalid format operation. Value '{0}' - " \
                        "Format '{1}'. Ignored."
                    LOGGER.warn(err_msg.format(self.value, self.style.format))
                    self.value_formatted = DataType.get_value(
                        'String', self.value)
            else:
                self.value_formatted = DataType.get_value('String', self.value)

        if self.can_grow:
            self._can_grow_height()

    def _can_grow_height(self):
        if self.value_formatted == '':
            return

        surface = cairo.SVGSurface(
            None, self.report.definition.Page.PageWidth,
            self.report.definition.Page.PageHeight)

        cr = cairo.Context(surface)

        name_fd = pango.FontDescription(self.style.font_family)
        name_fd.set_size(int(self.style.font_size * pango.SCALE))

        # Font style
        if self.style.font_style == 'Normal':
            name_fd.set_style(NuntiarePango.get_style('NORMAL'))
        elif self.style.font_style == 'Italic':
            name_fd.set_style(NuntiarePango.get_style('ITALIC'))

        # Font weight
        if self.style.font_weight in ('Lighter', '100', '200'):
            name_fd.set_weight(NuntiarePango.get_weight('ULTRALIGHT'))
        elif self.style.font_weight == '300':
            name_fd.set_weight(NuntiarePango.get_weight('LIGHT'))
        elif self.style.font_weight in ('Normal', '400', '500'):
            name_fd.set_weight(NuntiarePango.get_weight('NORMAL'))
        elif self.style.font_weight in ('Bold', '600', '700'):
            name_fd.set_weight(NuntiarePango.get_weight('BOLD'))
        elif self.style.font_weight in ('Bolder', '800'):
            name_fd.set_weight(NuntiarePango.get_weight('ULTRABOLD'))
        elif self.style.font_weight == '900':
            name_fd.set_weight(NuntiarePango.get_weight('HEAVY'))

        max_height = \
            self.height - self.style.padding_top - self.style.padding_bottom
        max_width = \
            self.width - self.style.padding_left - self.style.padding_right

        pc = NuntiarePango.get_pango_context(cr)
        layout = NuntiarePango.get_layout(pc)

        layout.set_width(int(max_width * pango.SCALE))
        layout.set_font_description(name_fd)

        if self.style.text_align in ('General', 'Left'):
            layout.set_alignment(NuntiarePango.get_alignment('LEFT'))
        elif self.style.text_align == 'Right':
            layout.set_alignment(NuntiarePango.get_alignment('RIGHT'))
        elif self.style.text_align == 'Center':
            layout.set_alignment(NuntiarePango.get_alignment('CENTER'))

        # TODO
        # if self.style.text_justify:
        #    layout.set_justify(True)

        NuntiarePango.layout_set_text(layout, self.value_formatted)
        text_w, text_h = NuntiarePango.layout_get_width_height(layout)

        text_height = text_h / pango.SCALE
        if text_height > max_height:
            self.set_new_height(
                text_height +
                self.style.padding_top +
                self.style.padding_bottom)
