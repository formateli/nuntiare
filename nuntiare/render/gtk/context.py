# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import cairo
import pango
import pangocairo
from nuntiare.pages.page_item import PageLine, PageRectangle, PageText, PageGrid
from nuntiare.pages.style import StyleItem
from nuntiare.tools import get_size_in_unit, raise_error_with_log, get_float_rgba

class Context(object):

    def __init__(self, report, surface_context, unit):
        super(Context, self).__init__()
        self.cr = surface_context
        self.unit = unit
        self.pages = report.pages

    def draw_header_style(self, header):
        self.draw_section_style(header, 
                get_size_in_unit(self.pages.margin_top, self.unit), 
                get_size_in_unit(self.pages.margin_left, self.unit), 
                get_size_in_unit(self.pages.header.height, self.unit),
                get_size_in_unit(self.pages.width - self.pages.margin_left - self.pages.margin_right, self.unit))

    def draw_body_style(self, body):
        self.draw_section_style(body, 
                get_size_in_unit(self.pages.margin_top + self.pages.header.height, self.unit), 
                get_size_in_unit(self.pages.margin_left, self.unit), 
                get_size_in_unit(self.pages.body.height, self.unit),
                get_size_in_unit(self.pages.width - self.pages.margin_left - self.pages.margin_right, self.unit))

    def draw_footer_style(self, footer):
        self.draw_section_style(footer, 
                get_size_in_unit(self.pages.height - self.pages.margin_bottom - self.pages.footer.height, self.unit), 
                get_size_in_unit(self.pages.margin_left, self.unit), 
                get_size_in_unit(self.pages.footer.height, self.unit),
                get_size_in_unit(self.pages.width - self.pages.margin_left - self.pages.margin_right, self.unit))


    def draw_items(self, it):

        if isinstance(it, PageLine):
            self.draw_line( it.style.border_color.default, 
                            it.style.border_style.default, 
                            it.style.border_width.default, 
                            get_size_in_unit(it.top, self.unit), get_size_in_unit(it.left, self.unit), 
                            get_size_in_unit(it.height, self.unit), get_size_in_unit(it.width, self.unit))

        if isinstance(it, PageText):
            text = it.value
            top = get_size_in_unit(it.top, self.unit)
            left = get_size_in_unit(it.left, self.unit)
            height = get_size_in_unit(it.height, self.unit)
            width = get_size_in_unit(it.width, self.unit)

            if not text or text=="":
                self.draw_rectangle(it.style, top, left, height, it.width)
                return

            padding_top = get_size_in_unit(it.style.text.padding_top.value, self.unit)
            padding_left = get_size_in_unit(it.style.text.padding_left.value, self.unit)
            padding_right = get_size_in_unit(it.style.text.padding_right.value, self.unit)
            padding_bottom = get_size_in_unit(it.style.text.padding_bottom.value, self.unit)
            max_height = height - padding_top - padding_bottom

            if max_height <= 0:
                raise_error_with_log("Textbox drawable height area must be greater than zero. See height and padding values.")

            font_sz = get_size_in_unit(it.style.text.font_size.value, 'pt')

            name_fd = pango.FontDescription(it.style.text.font_family)
            name_fd.set_size(font_sz * pango.SCALE)

            # Font style
            if it.style.text.font_style == 'Normal':
                name_fd.set_style(pango.STYLE_NORMAL)
            elif it.style.text.font_style == 'Italic':
                name_fd.set_style(pango.STYLE_ITALIC)

            # Font weight
            if it.style.text.font_weight == 'Lighter' or \
                    it.style.text.font_weight == '100' or \
                    it.style.text.font_weight == '200':
                name_fd.set_weight(pango.WEIGHT_ULTRALIGHT)
            elif it.style.text.font_weight == '300':
                name_fd.set_weight(pango.WEIGHT_LIGHT)
            elif it.style.text.font_weight == 'Normal' or \
                    it.style.text.font_weight == '400' or \
                    it.style.text.font_weight == '500':
                name_fd.set_weight(pango.WEIGHT_NORMAL)
            elif it.style.text.font_weight == 'Bold' or \
                    it.style.text.font_weight == '600' or \
                    it.style.text.font_weight == '700':
                name_fd.set_weight(pango.WEIGHT_BOLD)
            elif it.style.text.font_weight == 'Bolder' or \
                    it.style.text.font_weight == '800':
                name_fd.set_weight(pango.WEIGHT_ULTRABOLD)
            elif it.style.text.font_weight == '900':
                name_fd.set_weight(pango.WEIGHT_HEAVY)

            # TODO TextDecoration

            pc = pangocairo.CairoContext(self.cr)
            layout = pc.create_layout()
            layout.set_width(int((width - padding_left - padding_right) * pango.SCALE))
            layout.set_font_description(name_fd)

            if it.style.text.text_align == 'General' or it.style.text.text_align == 'Left':
                layout.set_alignment(pango.ALIGN_LEFT) 
            elif it.style.text.text_align == 'Right':
                layout.set_alignment(pango.ALIGN_RIGHT)
            elif it.style.text.text_align == 'Center':
                layout.set_alignment(pango.ALIGN_CENTER)
            elif it.style.text.text_align == 'Justify': # TODO Modify xml definition
                layout.set_justify(True) 

            layout.set_text(text)

            text_x, text_y, text_w, text_h = layout.get_extents()[1]

            rec_height = height

            #if it.can_grow and max_height < text_h / pango.SCALE:
            #    rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom
            #elif it.can_shrink and max_height > text_h / pango.SCALE:
            #    rec_height = (text_h / pango.SCALE) + padding_top + padding_bottom
            if not it.can_grow and not it.can_shrink and max_height < text_h / pango.SCALE:
                #TODO There must be a better way to do this.. Ex. Text clipping           
                while text_h / pango.SCALE > max_height:
                    line = layout.get_line(layout.get_line_count() - 1) # Get last line
                    text = text[:line.start_index - 1] # Remove last text
                    layout.set_text(text) # Set new text
                    text_x, text_y, text_w, text_h = layout.get_extents()[1]

            x = left + padding_left
            y = top + padding_top
            if it.style.text.vertical_align == 'Middle':
                y = y + ((max_height - (text_h / pango.SCALE)) / 2)
            elif it.style.text.vertical_align == 'Bottom':
                y = y + ((height - padding_bottom - (text_h / pango.SCALE)))

            self.draw_rectangle(it.style, top, left, rec_height, width)

            # Draw text
            self.set_color(it.style.text.color)
            self.cr.move_to(x, y)
            pc.show_layout(layout)

        if isinstance(it, PageRectangle):
            self.draw_rectangle(it.style, get_size_in_unit(it.top, self.unit), get_size_in_unit(it.left, self.unit), 
                     get_size_in_unit(it.height, self.unit), get_size_in_unit(it.width, self.unit))

        if isinstance(it, PageGrid):
            self.draw_rectangle(it.style, get_size_in_unit(it.top, self.unit), get_size_in_unit(it.left, self.unit), 
                     get_size_in_unit(it.height, self.unit), get_size_in_unit(it.width, self.unit))

    def draw_section_style(self, section, top, left, height, width):
        if not section or not section.style:
            return 
        return self.draw_rectangle(section.style, top, left, height, width)

    def draw_rectangle(self, style, top, left, height, width):
        self.cr.set_line_width(0.0)
        bg_color = self.set_color(style.background_color)
        if bg_color: # if not, background color is Transparent, nothing to draw
            self.cr.rectangle(left, top, width, height)
            self.cr.fill()
        self.draw_rectangle_borders(style, top, left, height, width)

    def draw_rectangle_borders(self, style, top, left, height, width):
        self.draw_line(style.border_color.top, 
                            style.border_style.top, 
                            style.border_width.top, 
                            top, left, 0, width)
        self.draw_line(style.border_color.left,
                            style.border_style.left,
                            style.border_width.left,
                            top, left, height, 0)
        self.draw_line(style.border_color.bottom,
                            style.border_style.bottom,
                            style.border_width.bottom,
                            top + height, left, 0, width)
        self.draw_line(style.border_color.right,
                            style.border_style.right,
                            style.border_width.right,
                            top, left + width, height, 0)

    def draw_line(self, color, border_style, border_width,
                top, left, height, width):

        bs = self.set_border_style(border_style)
        if bs == 'None':
            return # Nothing to draw

        self.set_color(color)
        self.set_border_width(border_width)

        self.cr.move_to(left, top)
        self.cr.rel_line_to(width, height)
        #self.cr.close_path()
        self.cr.stroke()

    def set_color(self, new_color):
        if not new_color:
            return None  
        # set color
        self.cr.set_source_rgba(get_float_rgba(new_color.red), 
                    get_float_rgba(new_color.green), 
                    get_float_rgba(new_color.blue),
                    get_float_rgba(new_color.alpha))
        return new_color.hex_alpha

    def set_border_style(self, new_border_style): 
        # Change current border_style
        st = new_border_style.value

        if st.lower() == 'solid' or st.lower() == 'none':
            self.cr.set_dash([])
            return st

        # TODO - for now, only resolve to 'Dotted' for others than None or Solid
        self.cr.set_dash([5.0])
        return st

    def set_border_width(self, new_border_width):
        # Change current border_width
        st = new_border_width.value
        self.cr.set_line_width(get_size_in_unit(st, self.unit))
        self.cr.set_line_cap(cairo.LINE_CAP_SQUARE)
        return st

