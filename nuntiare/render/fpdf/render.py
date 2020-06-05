# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from fpdf import FPDF
from nuntiare.definition.expression import Size
from nuntiare.definition.element import EmbeddedImage
from .. render import Render
from ... import LOGGER

TEST = True

class FPdfRender(Render):
    def __init__(self):
        super(FPdfRender, self).__init__(extension='pdf')

    def render(self, report, **kws):
        super(FPdfRender, self).render(report, **kws)

        result = report.result

        orientation = 'P'
        format_ = (result.width, result.height)
        if result.width > result.height:
            orientation = 'L'
            format_ = (result.height, result.width)

        self._pdf = FPDF(orientation=orientation,
                         unit='pt', format=format_)
        author = report.definition.Author
        if author is not None:
            self._pdf.set_author(author)
        self._pdf.set_creator('Nuntiare Report Tollkit - https://formateli.com')
        self._pdf.set_auto_page_break(False)

        self._pdf.set_margins(0, 0)
        #print(self._pdf.t_margin)
        #print(self._pdf.b_margin)

        self._pdf.add_page()
        self._pdf.set_xy(0, 0)

        if TEST:
            self._draw_rectangle(
                result.margin_left, result.margin_top,
                result.width - result.margin_left - result.margin_right,
                result.height - result.margin_top - result.margin_bottom,
                draw=(0, 0, 0), plus_margins=False)

        self._render_items(result.body.items.item_list)

#        self._draw_rectangle(50, 50, 100, 50, fill=(0, 255, 0))
#        self._pdf.set_xy(50, 50)
#        self._pdf.set_font("Arial", size=12)
#        self._pdf.cell(200, 10, txt="Welcome to Python!", ln=1)

        self._pdf.output(self.result_file)

    def _render_items(self, items):
        if not items:
            return

        for it in items:
            if it.type == 'PageImage':
                self._draw_image(it)
            else:
                continue

    def _draw_image(self, it):
        width = it.width
        height = it.height
        image_width = None
        image_height = None

        file_ = EmbeddedImage.get_pil_image_io_from_base64(
            it.image_base64, it.mimetype)

        if it.image_sizing == 'AutoSize':
            width = self._px2pt(it.image_width)
            height = self._px2pt(it.image_height)
        elif it.image_sizing == 'Fit':
            pass
        elif it.image_sizing == 'FitProportional':
            width, height = EmbeddedImage.get_proportional_size(
                    it.width, it.height,
                    it.image_width,
                    it.image_height)

        self._draw_rectangle(
            it.left, it.top,
            it.width, it.height,
            fill=it.style.background_color,
            draw=(0, 0, 0),
            )

        if file_ is not None:
            self._pdf.image(
                file_,
                self.report.result.margin_left + it.left,
                self.report.result.margin_top + it.top,
                width, height, type='png'
                )

    def _draw_rectangle(self, left, top, width, height,
                        fill=None, draw=None, line_width=None,
                        plus_margins=True):
        res = ''
        if plus_margins:
            top += self.report.result.margin_top
            left += self.report.result.margin_left

        if draw is not None:
            res += 'D'
            self._pdf.set_draw_color(
                draw[0], draw[1], draw[2])
            if line_width is None:
                self._pdf.set_line_width(1)
            else:
                self._pdf.set_line_width(line_width)
        if fill is not None:
            res += 'F'
            self._pdf.set_fill_color(
                fill[0], fill[1], fill[2])
        self._pdf.rect(left, top, width, height, res)

    def _pt2px(self, val):
        return Size.convert_to_pixel(val, 'pt')

    def _px2pt(self, val):
        return Size.convert_from_pixel(val, 'pt')

    def help(self):
        'FPdfRender help'
