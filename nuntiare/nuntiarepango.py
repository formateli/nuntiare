# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

TYPE_ = None # None, GTK, GI

try:
    import pango
    import pangocairo
    TYPE_ = 'GTK'
except ImportError:
    from gi.repository import Pango as pango
    from gi.repository import PangoCairo as pangocairo
    TYPE_ = 'GI'


class NuntiarePango(object):
    @staticmethod
    def get_style(value):
        if TYPE_ == 'GI':
            return getattr(pango.Style, value)
        elif TYPE_ == 'GTK':
            return getattr(pango, 'STYLE_' + value)
            

    @staticmethod
    def get_weight(value):
        if TYPE_ == 'GI':
            return getattr(pango.Weight, value)
        elif TYPE_ == 'GTK':
            return getattr(pango, 'WEIGHT_' + value)

    @staticmethod
    def get_alignment(value):
        if TYPE_ == 'GI':
            return getattr(pango.Alignment, value)
        elif TYPE_ == 'GTK':
            return getattr(pango, 'ALIGN_' + value)

    @staticmethod
    def get_pango_context(cr):
        if TYPE_ == 'GI':
            pc = pangocairo.create_context(cr)
        elif TYPE_ == 'GTK':
            pc = pangocairo.CairoContext(cr)
        return pc

    @staticmethod
    def get_layout(pango_context):
        if TYPE_ == 'GI':
            return pango.Layout.new(pango_context)
        elif TYPE_ == 'GTK':
            return pango_context.create_layout()

    @staticmethod
    def layout_set_text(layout, text):
        if TYPE_ == 'GI':
            layout.set_text(text, -1)
        elif TYPE_ == 'GTK':
            layout.set_text(text)

    @staticmethod
    def layout_show(layout, pc, cr):
        if TYPE_ == 'GI':
            pangocairo.show_layout(cr, layout)
        elif TYPE_ == 'GTK':
            pc.show_layout(layout)

    @staticmethod
    def layout_get_width_height(layout):
        if TYPE_ == 'GI':
            rec = layout.get_extents()[1]
            width = rec.width
            height = rec.height
        elif TYPE_ == 'GTK':
            x, y, width, height = layout.get_extents()[1]
        return width, height
