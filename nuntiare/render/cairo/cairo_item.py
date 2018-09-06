# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import cairo
from ... definition.expression import Color
#from ... nuntiarepango import pango, NuntiarePango
from ... import FontManager
from ... import LOGGER


class CairoItem(object):
    def __init__(self, item, parent=None):
        self.parent = parent
        self.children = []
        # Nuntiare outcome object
        self.item = item
        self.keep_together = \
            item.keep_together if hasattr(item, 'keep_together') else None
        self.original_top = item.original_top
        self.original_left = item.original_left
        self.original_height = item.original_height
        self.original_width = item.original_width
        self.top = item.top
        self.left = item.left
        self.height = item.height
        self.width = item.width
        self.section_top = 0.0
        self.y_minus = 0.0
        self.x_minus = 0.0
        # Ready to be placed in a frame
        self.checked = False
        # Already placed in a frame
        self.placed = False
        # It is an extention of an item
        # that not fits in previous frame width
        self.horizontal_extention = False

        if item.items_info:
            for it in item.items_info.item_list:
                c_it = CairoItem(it, parent=self)
                self.children.append(c_it)

    @classmethod
    def start_clip_area(cls, ctx, top, left, width, height, style):
        def half_line_width(width):
            if width is None or width == 0:
                return 0.0
            return width / 2

        b_top = 0.0
        b_bottom = 0.0
        b_right = 0.0
        b_left = 0.0
        if style:
            b_top = half_line_width(style.top_border.width)
            b_bottom = half_line_width(style.bottom_border.width)
            b_right = half_line_width(style.right_border.width)
            b_left = half_line_width(style.left_border.width)

        ctx.save()
        ctx.rectangle(
            left + b_left,
            top + b_top,
            width - (b_right + b_left),
            height - (b_top + b_bottom))
        ctx.clip()

    @classmethod
    def finish_clip_area(cls, ctx):
        ctx.restore()

    def clone(self):
        ci = CairoItem(self.item)
        ci.top = self.top
        ci.height = self.height
        self.clone_children(ci, self.children)
        return ci

    def clone_children(self, ci, children):
        i = 0
        for child in children:
            ci.children[i].top = child.top
            ci.children[i].height = child.height
            ci.children[i].keep_together = child.keep_together
            self.clone_children(ci.children[i], child.children)
            i += 1

    def draw(self, ctx, x, y):
        x -= self.x_minus
        y -= self.y_minus
        if self.parent:
            x += self.parent.left
            y += self.parent.top - self.parent.section_top

        ctx.translate(x, y)
        top = self.top - self.section_top

        if self.item.type == 'PageLine':
            self._draw_line(
                ctx,
                self.item.style._border.color,
                self.item.style._border.border_style,
                self.item.style._border.width,
                top, self.left,
                self.height, self.width)

        elif self.item.type == 'PageRectangle':
            self._draw_rectangle(
                ctx, self.item.style, top, self.left,
                self.height, self.width)

            if self.children:
                self.start_clip_area(
                    ctx, top, self.left,
                    self.width, self.height,
                    self.item.style)
                for child in self.children:
                    ctx.identity_matrix()
                    child.draw(ctx, x, y)
                self.finish_clip_area(ctx)

        elif self.item.type == 'PageText':
            self._draw_textbox(ctx, top, self.item)

        ctx.identity_matrix()

    @classmethod
    def _draw_textbox(cls, ctx, top, item):
        text = item.value_formatted
        if text is None or text == '':
            # Draw an empty rectangle
            cls._draw_rectangle(
                ctx, item.style, top, item.left,
                item.height)
            return

        pango = FontManager.get_pango

        max_height = \
            item.height - item.style.padding_top - item.style.padding_bottom
        max_width = \
            item.width - item.style.padding_left - item.style.padding_right

        font_desc = cls._get_font_description(item)
        layout, pango_ctx = cls._get_pango_layout(
            ctx, item, font_desc, max_width)

        FontManager.layout_set_text(layout, text)
        text_w, text_h = FontManager.layout_get_width_height(layout)

        text_height = text_h / pango('SCALE')
        text_width = text_w / pango('SCALE')

        if text_height > max_height or text_width > max_width:
            if text_height > max_height:
                text_height = max_height
            if text_width > max_width:
                text_width = max_width

        text_x = item.left + item.style.padding_left
        text_y = top + item.style.padding_top
        if item.style.vertical_align == 'Middle':
            text_y += (max_height - text_height) / 2
        elif item.style.vertical_align == 'Bottom':
            text_y += \
                max_height - item.style.padding_bottom - text_height

        cls._draw_rectangle(
            ctx, item.style, top, item.left,
            item.height, item.width)

        cls.start_clip_area(
            ctx, top, item.left,
            item.width, item.height,
            item.style)

        cls._set_color(ctx, item.style.color)

        cls.start_clip_area(
            ctx, top + item.style.padding_top,
            item.left + item.style.padding_left,
            max_width, max_height,
            None)

        ctx.move_to(text_x, text_y)

        FontManager.layout_show(layout, pango_ctx, ctx)

        cls.finish_clip_area(ctx)
        cls.finish_clip_area(ctx)

    @classmethod
    def _draw_rectangle(
            cls, ctx, style, top, left, height, width):
        ctx.set_line_width(0.0)
        bg_color = cls._set_color(ctx, style.background_color)
        if bg_color:
            ctx.rectangle(left, top, width, height)
            ctx.fill()
        cls._draw_rectangle_borders(
            ctx, style, top, left, height, width)

    @classmethod
    def _draw_rectangle_borders(
            cls, ctx, style, top, left, height, width):
        cls._draw_line(
            ctx,
            style.top_border.color,
            style.top_border.border_style,
            style.top_border.width,
            top, left, 0.0, width)
        cls._draw_line(
            ctx,
            style.left_border.color,
            style.left_border.border_style,
            style.left_border.width,
            top, left, height, 0.0)
        cls._draw_line(
            ctx,
            style.bottom_border.color,
            style.bottom_border.border_style,
            style.bottom_border.width,
            top + height, left, 0.0, width)
        cls._draw_line(
            ctx,
            style.right_border.color,
            style.right_border.border_style,
            style.right_border.width,
            top, left + width, height, 0.0)

    @classmethod
    def _draw_line(
            cls, ctx, color, border_style,
            border_width, top, left,
            height, width):
        if border_style is None:
            bs = 'none'
        else:
            bs = border_style.lower()
        cls._set_border_style(ctx, bs)
        if bs == 'none' or border_width is None:
            return  # Nothing to draw
        cls._set_color(ctx, color)
        cls._set_border_width(ctx, border_width)
        ctx.move_to(left, top)
        ctx.rel_line_to(width, height)
        ctx.stroke()

    @classmethod
    def _set_color(cls, ctx, new_color):
        if not new_color:
            return
        rgb = Color.to_rgb(new_color)
        ctx.set_source_rgba(
            float(rgb[0]) / float(65535),
            float(rgb[1]) / float(65535),
            float(rgb[2]) / float(65535),
            1.0)
        return new_color

    @classmethod
    def _set_border_style(cls, ctx, border_name):
        if border_name in ('solid', 'none'):
            if border_name == 'solid':
                ctx.set_dash([])
            return

        # TODO
        # for now, only resolve to 'Dotted'
        # for others than None or Solid
        ctx.set_dash([5.0])

    @classmethod
    def _set_border_width(cls, ctx, new_border_width):
        ctx.set_line_width(new_border_width)
        ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
        return new_border_width

    @classmethod
    def _get_font_description(cls, it):
        pango = FontManager.get_pango

        font_desc = pango('FontDescription')(
            it.style.font_family)
        font_desc.set_size(
            int(it.style.font_size * pango('SCALE')))

        # Font style
        if it.style.font_style == 'Normal':
            style = FontManager.get_style('NORMAL')
        elif it.style.font_style == 'Italic':
            style = FontManager.get_style('ITALIC')
        font_desc.set_style(style)

        # Font weight
        if it.style.font_weight in ('Lighter', '100', '200'):
            weight = FontManager.get_weight('ULTRALIGHT')
        elif it.style.font_weight == '300':
            weight = FontManager.get_weight('LIGHT')
        elif it.style.font_weight in ('Normal', '400', '500'):
            weight = FontManager.get_weight('NORMAL')
        elif it.style.font_weight in ('Bold', '600', '700'):
            weight = FontManager.get_weight('BOLD')
        elif it.style.font_weight in ('Bolder', '800'):
            weight = FontManager.get_weight('ULTRABOLD')
        elif it.style.font_weight == '900':
            weight = FontManager.get_weight('HEAVY')
        font_desc.set_weight(weight)

        # TODO TextDecoration

        return font_desc

    @classmethod
    def _get_pango_layout(cls, ctx, it, font_desc, max_width):
        pango = FontManager.get_pango

        pango_ctx = FontManager.get_pango_context(ctx)
        layout = FontManager.get_layout(pango_ctx)

        layout.set_width(int(max_width * pango('SCALE')))
        layout.set_font_description(font_desc)

        if it.style.text_align in ('General', 'Left'):
            alignment = FontManager.get_alignment('LEFT')
        elif it.style.text_align == 'Right':
            alignment = FontManager.get_alignment('RIGHT')
        elif it.style.text_align == 'Center':
            alignment = FontManager.get_alignment('CENTER')
        else:
            alignment = FontManager.get_alignment('LEFT')
        layout.set_alignment(alignment)

        # TODO
#        if it.style.text_justify:
#            layout.set_justify(True)

        return layout, pango_ctx
