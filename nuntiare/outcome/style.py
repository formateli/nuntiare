# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from .. definition.expression import Size


class OutcomeStyle(object):
    '''
    Style cache. Must be one instance per report.
    See: nuntiare.report.Report
    '''

    _count = 0
    _styles = {}

    def __init__(self, report):
        self._report = report
        self.styles = {}
        # Used when style_def = None
        self.first_key = None

    def get_style(self, style_def):
        if not style_def and self.first_key:
            return self.styles[self.first_key]
        style = _StyleInfo()
        style.background_color = self._report.get_value(
                style_def, "BackgroundColor", None)
        style.background_gradient_type = self._report.get_value(
                style_def, "BackgroundGradientType", 'None')
        style.background_gradient_end_color = self._report.get_value(
                style_def, "BackgroundGradientEndColor", None)
        style.background_image = None  # TODO
        style.font_style = self._report.get_value(
                style_def, "FontStyle", 'Normal')
        style.font_family = self._report.get_value(
                style_def, "FontFamily", 'Arial')
        style.font_size = self._report.get_value(
                style_def, "FontSize", Size.convert(10, 'pt'))
        style.font_weight = self._report.get_value(
                style_def, "FontWeight", 'Normal')
        style.format = self._report.get_value(
                style_def, "Format", None)
        style.text_decoration = self._report.get_value(
                style_def, "TextDecoration", 'None')
        style.text_align = self._report.get_value(
                style_def, "TextAlign", 'General')
        style.vertical_align = self._report.get_value(
                style_def, "VerticalAlign", 'Top')
        style.color = self._report.get_value(
                style_def, "Color", '#000000')
        style.padding_left = self._report.get_value(
                style_def, "PaddingLeft", 0.0)
        style.padding_right = self._report.get_value(
                style_def, "PaddingRight", 0.0)
        style.padding_top = self._report.get_value(
                style_def, "PaddingTop", 0.0)
        style.padding_bottom = self._report.get_value(
                style_def, "PaddingBottom", 0.0)
        style.line_height = self._report.get_value(
                style_def, "LineHeight", Size.convert(1, 'pt'))
        style.direction = self._report.get_value(
                style_def, "Direction", 'LTR')
        style.writing_mode = self._report.get_value(
                style_def, "WritingMode", 'Horizontal')

        if style_def:
            self._get_border(
                style._border, style_def.get_element("Border"))
            self._get_border(
                style.top_border, style_def.get_element("TopBorder"))
            self._get_border(
                style.bottom_border, style_def.get_element("BottomBorder"))
            self._get_border(
                style.left_border, style_def.get_element("LeftBorder"))
            self._get_border(
                style.right_border, style_def.get_element("RightBorder"))

        str_id = style.get_id()
        if str_id in self.styles:
            return self.styles[str_id]
        if str_id in OutcomeStyle._styles:
            self.styles[str_id] = OutcomeStyle._styles[str_id]
            return OutcomeStyle._styles[str_id]
        style.id = OutcomeStyle._count
        OutcomeStyle._count = OutcomeStyle._count + 1
        OutcomeStyle._styles[str_id] = style
        self.styles[str_id] = style
        if not self.first_key:
            self.first_key = str_id
        return style

    def _get_border(self, border, border_def):
        if not border_def:
            return
        border.color = self._report.get_value(
                border_def, "Color", None)
        border.border_style = self._report.get_value(
                border_def, "BorderStyle", None)
        border.Width = self._report.get_value(
                border_def, "Width", None)


class _StyleInfo(object):
    class Border(object):
        def __init__(self, color=None, style=None, width=None):
            self._str_id = None
            self.color = color
            self.border_style = style
            self.width = width

        def get_id(self):
            self._str_id = None
            self._add_id(self.color)
            self._add_id(self.border_style)
            self._add_id(self.width)
            return self._str_id

        def _add_id(self, value):
            if self._str_id is None:
                self._str_id = "|"
            else:
                self._str_id = self._str_id + "-"
            if value:
                self._str_id = self._str_id + str(value)

    def __init__(self):
        self.id = None
        self._str_id = None
        self._border = _StyleInfo.Border(
                "#000000", 'None', Size.convert(1, 'pt'))
        self.top_border = _StyleInfo.Border()
        self.bottom_border = _StyleInfo.Border()
        self.left_border = _StyleInfo.Border()
        self.right_border = _StyleInfo.Border()
        self.background_color = None
        self.background_gradient_type = None
        self.background_gradient_end_color = None
        self.background_image = None
        self.font_style = None
        self.font_family = None
        self.font_size = None
        self.font_weight = None
        self.format = None
        self.text_decoration = None
        self.text_align = None
        self.vertical_align = None
        self.color = None
        self.padding_left = None
        self.padding_right = None
        self.padding_top = None
        self.padding_bottom = None
        self.line_height = None
        self.direction = None
        self.writing_mode = None

    def get_id(self):
        self._str_id = None
        self._add_id(self.background_color)
        self._add_id(self.background_gradient_type)
        self._add_id(self.background_gradient_end_color)
        self._add_id(self.background_image)
        self._add_id(self.font_style)
        self._add_id(self.font_family)
        self._add_id(self.font_size)
        self._add_id(self.font_weight)
        self._add_id(self.format)
        self._add_id(self.text_decoration)
        self._add_id(self.text_align)
        self._add_id(self.vertical_align)
        self._add_id(self.color)
        self._add_id(self.padding_left)
        self._add_id(self.padding_right)
        self._add_id(self.padding_top)
        self._add_id(self.padding_bottom)
        self._add_id(self.line_height)
        self._add_id(self.direction)
        self._add_id(self.writing_mode)
        self._add_border_id(self.top_border)
        self._add_border_id(self.bottom_border)
        self._add_border_id(self.left_border)
        self._add_border_id(self.right_border)
        return self._str_id

    def _add_id(self, value):
        if not value:
            self._add_id_value("")
        else:
            self._add_id_value(str(value))

    def _add_border_id(self, border):
        if not border.color:
            border.color = self._border.color
        if not border.border_style:
            border.border_style = self._border.border_style
        if not border.width:
            border.width = self._border.width
        self._add_id_value(border.get_id())

    def _add_id_value(self, value):
        if self._str_id is None:
            self._str_id = value
        else:
            self._str_id = self._str_id + "-" + value
