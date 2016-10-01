# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

is_gi = False
try:
    import pango
    import pangocairo
except ImportError:
    from gi.repository import Pango as pango
    from gi.repository import PangoCairo as pangocairo
    is_gi = True


class NuntiarePango(object):
    @staticmethod
    def get_style(value):
        if is_gi:
            return getattr(pango.Style, value)
        else:
            return getattr(pango, 'STYLE_' + value)

    @staticmethod
    def get_weight(value):
        if is_gi:
            return getattr(pango.Weight, value)
        else:
            return getattr(pango, 'WEIGHT_' + value)

    @staticmethod
    def get_alignment(value):
        if is_gi:
            return getattr(pango.Alignment, value)
        else:
            return getattr(pango, 'ALIGN_' + value)

    @staticmethod
    def get_pango_context(cr):
        if is_gi:
            pc = pangocairo.create_context(cr)
        else:
            pc = pangocairo.CairoContext(cr)
        return pc

    @staticmethod
    def get_layout(pango_context):
        if is_gi:
            return pango.Layout.new(pango_context)
        else:
            return pango_context.create_layout()

    @staticmethod
    def layout_set_text(layout, text):
        if is_gi:
            layout.set_text(text, -1)
        else:
            layout.set_text(text)

    @staticmethod
    def layout_show(layout, pc, cr):
        if is_gi:
            pangocairo.show_layout(cr, layout)
        else:
            pc.show_layout(layout)

    @staticmethod
    def layout_get_width_height(layout):
        if is_gi:
            rec = layout.get_extents()[1]
            width = rec.width
            height = rec.height
        else:
            x, y, width, height = layout.get_extents()[1]
        return width, height
