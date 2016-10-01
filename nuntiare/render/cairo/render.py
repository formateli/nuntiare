# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import cairo
from . pages import Pages
from . cairo_item import CairoItem
from .. render import Render
from ... import LOGGER


class CairoRender(Render):
    def __init__(self, extension):
        super(CairoRender, self).__init__(extension=extension)
        self.surface = None
        self.pages = None  # public for test purposes

    def render(self, report, overwrite):
        super(CairoRender, self).render(report, overwrite)

        result = report.result

        # TODO. For test purposes.
        # It should be an option for
        # comand line utility
        show_limits = False

        self.pages = Pages(report)

        if self.extension == 'pdf':
            self.surface = cairo.PDFSurface(
                self.result_file, result.width, result.height)
        elif self.extension == 'svg':
            self.surface = cairo.SVGSurface(
                self.result_file, result.width, result.height)

        ctx = cairo.Context(self.surface)

        page_top = result.margin_top
        footer_top = result.margin_top + result.body.available_height
        if result.header:
            page_top += result.header.height
            footer_top += result.header.height

        for page in self.pages.pages:
            # Print body style
            CairoItem._draw_rectangle(
                ctx, result.body.style,
                page_top, result.margin_left,
                result.body.available_height,
                result.available_width)
            CairoItem.start_clip_area(
                ctx, page_top, result.margin_left,
                result.available_width,
                result.body.available_height,
                result.body.style)

            for f in page.frames:
                frame_left = f.left + result.margin_left
                ctx.set_line_width(0.5)

                if show_limits:
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.rectangle(
                        frame_left,
                        page_top,
                        f.drawable_width,
                        f.height)
                    ctx.stroke()

                CairoItem.start_clip_area(
                    ctx, page_top, frame_left,
                    f.drawable_width, f.height,
                    None)

                self._print_items(
                    ctx, f.cairo_items,
                    page_top, frame_left)

                CairoItem.finish_clip_area(ctx)

            CairoItem.finish_clip_area(ctx)

            if result.header:
                self._print_header_footer(
                    ctx, page.header, show_limits,
                    result.margin_left,
                    result.margin_top,
                    result.available_width)

            if result.footer:
                self._print_header_footer(
                    ctx, page.footer, show_limits,
                    result.margin_left,
                    footer_top,
                    result.available_width)

            self.surface.show_page()

        self.surface.finish()

    def _print_header_footer(
            self, ctx, header_footer, show_limits,
            left, top, width):

        if not header_footer:
            return

        if show_limits:
            ctx.set_line_width(0.5)
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(
                left, top, width,
                header_footer.height)
            ctx.stroke()

        # Print style
        CairoItem._draw_rectangle(
            ctx, header_footer.definition.style,
            top, left,
            header_footer.definition.available_height,
            width)

        CairoItem.start_clip_area(
            ctx, top, left,
            width, header_footer.height,
            header_footer.definition.style)

        self._print_items(
            ctx, header_footer.cairo_items, top, left)

        CairoItem.finish_clip_area(ctx)

    def _print_items(self, ctx, items, top, left):
        for it in items:
            it.draw(ctx, left, top)
