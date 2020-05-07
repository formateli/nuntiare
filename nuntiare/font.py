# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

_TYPE = None  # None, GTK, GI

try:
    import cairo
    import pango
    import pangocairo
    _TYPE = 'GTK'
except ImportError:
    try:
        import gi
        import cairo
        gi.require_version('Pango', '1.0')
        gi.require_version('PangoCairo', '1.0')
        from gi.repository import Pango as pango
        from gi.repository import PangoCairo as pangocairo
        _TYPE = 'GI'
    except ImportError:
        pass


class IFontManager(object):
    @staticmethod
    def get_name():
        raise NotImplementedError('get_name')

    @staticmethod
    def get_description():
        raise NotImplementedError('get_description')

    @staticmethod
    def get_text_height(text, page, cur_width, cur_height, style):
        raise NotImplementedError('get_text_height')


class FontManager(object):
    @staticmethod
    def _get_font_manager():
        if _TYPE is None:
            return NuntiareFont
        else:
            return CairoFont


class NuntiareFont(IFontManager):
    @staticmethod
    def get_name():
        return 'NuntiareFont'

    @staticmethod
    def get_description():
        return 'Nuntiare default Font Manager'

    @staticmethod
    def get_text_height(text, page, cur_width, cur_height, style):
        return cur_height - style.padding_top - style.padding_bottom


class CairoFont(IFontManager):
    @staticmethod
    def get_name():
        return 'CairoFont'

    @staticmethod
    def get_description():
        return 'Nuntiare Cairo Font Manager'

    @staticmethod
    def get_text_height(text, page, cur_width, cur_height, style):
        surface = cairo.SVGSurface(
            None, page.PageWidth, page.PageHeight)

        cr = cairo.Context(surface)

        name_fd = pango.FontDescription(style.font_family)
        name_fd.set_size(int(style.font_size * pango.SCALE))

        # Font style
        if style.font_style == 'Normal':
            name_fd.set_style(CairoFont.get_style('NORMAL'))
        elif style.font_style == 'Italic':
            name_fd.set_style(CairoFont.get_style('ITALIC'))

        # Font weight
        if style.font_weight in ('Lighter', '100', '200'):
            name_fd.set_weight(CairoFont.get_weight('ULTRALIGHT'))
        elif style.font_weight == '300':
            name_fd.set_weight(CairoFont.get_weight('LIGHT'))
        elif style.font_weight in ('Normal', '400', '500'):
            name_fd.set_weight(CairoFont.get_weight('NORMAL'))
        elif style.font_weight in ('Bold', '600', '700'):
            name_fd.set_weight(CairoFont.get_weight('BOLD'))
        elif style.font_weight in ('Bolder', '800'):
            name_fd.set_weight(CairoFont.get_weight('ULTRABOLD'))
        elif style.font_weight == '900':
            name_fd.set_weight(CairoFont.get_weight('HEAVY'))

        max_width = \
            cur_width - style.padding_left - style.padding_right

        pc = CairoFont.get_pango_context(cr)
        layout = CairoFont.get_layout(pc)

        layout.set_width(int(max_width * pango.SCALE))
        layout.set_font_description(name_fd)

        if style.text_align in ('General', 'Left'):
            layout.set_alignment(CairoFont.get_alignment('LEFT'))
        elif style.text_align == 'Right':
            layout.set_alignment(CairoFont.get_alignment('RIGHT'))
        elif style.text_align == 'Center':
            layout.set_alignment(CairoFont.get_alignment('CENTER'))

        # TODO
        # if style.text_justify:
        #    layout.set_justify(True)

        CairoFont.layout_set_text(layout, text)
        text_w, text_h = CairoFont.layout_get_width_height(layout)

        text_height = text_h / pango.SCALE

        return text_height

    @staticmethod
    def get_pango(name):
        return getattr(pango, name)

    @staticmethod
    def get_style(value):
        if _TYPE == 'GI':
            return getattr(pango.Style, value)
        else:
            return getattr(pango, 'STYLE_' + value)

    @staticmethod
    def get_weight(value):
        if _TYPE == 'GI':
            return getattr(pango.Weight, value)
        else:
            return getattr(pango, 'WEIGHT_' + value)

    @staticmethod
    def get_alignment(value):
        if _TYPE == 'GI':
            return getattr(pango.Alignment, value)
        else:
            return getattr(pango, 'ALIGN_' + value)

    @staticmethod
    def get_pango_context(cr):
        if _TYPE == 'GI':
            pc = pangocairo.create_context(cr)
        else:
            pc = pangocairo.CairoContext(cr)
        return pc

    @staticmethod
    def get_layout(pango_context):
        if _TYPE == 'GI':
            return pango.Layout.new(pango_context)
        else:
            return pango_context.create_layout()

    @staticmethod
    def layout_set_text(layout, text):
        if _TYPE == 'GI':
            layout.set_text(text, -1)
        else:
            layout.set_text(text)

    @staticmethod
    def layout_show(layout, pc, cr):
        if _TYPE == 'GI':
            pangocairo.show_layout(cr, layout)
        else:
            pc.show_layout(layout)

    @staticmethod
    def layout_get_width_height(layout):
        if _TYPE == 'GI':
            rec = layout.get_extents()[1]
            width = rec.width
            height = rec.height
        else:
            x, y, width, height = layout.get_extents()[1]
        return width, height
