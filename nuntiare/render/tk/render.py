# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from nuntiare.definition.expression import Size
from nuntiare.definition.element import EmbeddedImage
from nuntiare.pluma.view.designer.report_item import ReportItem
from .. render import Render
from ... import LOGGER

TEST = True


class TkRender(Render):

    _images = []

    def __init__(self):
        super(TkRender, self).__init__()

    def render(self, report, canvas):
        self._canvas = canvas
        super(TkRender, self).render(report, None)

        result = report.result

        self._render_items(result.body.items.item_list)

    def _render_items(self, items):
        if not items:
            return

        for it in items:
            print(it.type)
            if it.type == 'PageImage':
                self._draw_image(it)
            elif it.type == 'PageRectangle':
                self._draw_rectangle_item(it)
            elif it.type == 'PageText':
                self._draw_text(it)
            elif it.type == 'PageLine':
                self._draw_line(it)
            else:
                continue

    def _draw_text(self, it):
        left = self._pt_2_px(it.cumulative_left())
        top = self._pt_2_px(it.cumulative_top())
        width = self._pt_2_px(it.width)
        height = self._pt_2_px(it.height)

        self._draw_rectangle(
            left, top, width, height,
            it.style
            )

        anchor, justify = ReportItem.get_text_justify(
                it.style.text_align, it.style.vertical_align)
        label = ttk.Label(
            self._canvas,
            text=it.value,
            anchor=anchor,
            justify=justify,
            style=ReportItem.get_label_style(
                it.style.background_color, it.style.color),
            font=ReportItem.get_font(
                family=it.style.font_family,
                size=self._pt_2_px(it.style.font_size),
                weight=it.style.font_weight,
                style=it.style.font_style,
                decoration=it.style.text_decoration
                ),
            wraplength=self._pt_2_px(it.width)
            )

        label.grid(row=0, column=0, sticky='nwes')

        self._canvas.create_window(
            left, top, window=label, anchor='nw',
            width=width,
            height=height
            )

    def _draw_rectangle_item(self, it):
        self._draw_rectangle(
            self._pt_2_px(it.cumulative_left()),
            self._pt_2_px(it.cumulative_top()),
            self._pt_2_px(it.width),
            self._pt_2_px(it.height),
            it.style
            )
        self._render_items(
            it.items_info.item_list)

    def _draw_line(self, it):
        left = self._pt_2_px(it.cumulative_left())
        top = self._pt_2_px(it.cumulative_top())
        self._canvas.create_line(
            left, top,
            left + self._pt_2_px(it.width),
            top + self._pt_2_px(it.height),
            fill=it.style.top_border.color,
            width=it.style.top_border.width
            )

    def _draw_image(self, it):
        width = it.width
        height = it.height
        image_width = None
        image_height = None

        resize = None

        if it.image_sizing == 'AutoSize':
            width = self._pt_2_px(it.image_width)
            height = self._pt_2_px(it.image_height)
        elif it.image_sizing == 'Fit':
            resize = (self._pt_2_px(width),
                      self._pt_2_px(height))
        elif it.image_sizing == 'FitProportional':
            wd, hg = EmbeddedImage.get_proportional_size(
                    it.width, it.height,
                    it.image_width,
                    it.image_height)
            resize = (
                self._pt_2_px(wd),
                self._pt_2_px(hg))

        self._draw_rectangle(
            self._pt_2_px(it.left),
            self._pt_2_px(it.top),
            self._pt_2_px(width),
            self._pt_2_px(height),
            it.style
            )

        if resize is not None:
            img = EmbeddedImage.get_pil_image_from_base64(
                    it.image_base64)
            pil_img = img.resize(resize)
        else:
            pil_img = EmbeddedImage.get_pil_image_from_base64(
                    it.image_base64)
        image = ImageTk.PhotoImage(pil_img)

        self._canvas.create_image(
            self._pt_2_px(it.left),
            self._pt_2_px(it.top),
            image=image,
            anchor='nw',
            )

        if not image in self._images:
            self._images.append(image)  # Avoid garbage collection

    def _draw_rectangle(self, left, top, width, height, style):
        self._canvas.create_rectangle(
                left, top,
                left + width, top + height,
                fill=style.background_color,
                width=1.0 if TEST else 0)

    @staticmethod
    def _pt_2_px(value):
        return Size.convert(value, 'pt', 'px')

    def help(self):
        'Tk canvas Render help'
