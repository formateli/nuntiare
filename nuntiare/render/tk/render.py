# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from PIL import ImageTk
from nuntiare.definition.expression import Size
from nuntiare.definition.element import EmbeddedImage
from .. render import Render
from ... import LOGGER

TEST = True

class TkRender(Render):

    _images = []

    def __init__(self):
        super(TkRender, self).__init__()

    def render(self, report, canvas):
        super(TkRender, self).render(report)

        self._canvas = canvas
        self._ppi = self._canvas.winfo_pixels('1i')

        result = report.result

        self._render_items(result.body.items.item_list)

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

        if it.image_source == 'Embedded':
            el = self.report.definition.EmbeddedImages
            imgem = el.embedded_images[it.image_value]
            data = imgem.ImageData
            image_width = imgem.image_width
            image_height = imgem.image_height
        elif it.image_source == 'External':
            file_ = self.report.find_file(it.image_value)
            data = None
            if file_ is not None:
                imgem = EmbeddedImage.get_base64_image(
                    file_, it.name, it.mimetype)
                data = imgem[2]
                image_width = imgem[3].width
                image_height = imgem[3].height

        resize = None

        if it.image_sizing == 'AutoSize':
            width = self._px2pt(image_width)
            height = self._px2pt(image_height)
        elif it.image_sizing == 'Fit':
            resize = (int(self._pt2px(width)),
                      int(self._pt2px(height)))
        elif it.image_sizing == 'FitProportional':
            wd, hg = EmbeddedImage.get_proportional_size(
                    it.width, it.height,
                    image_width,
                    image_height)
            resize = (
                int(self._pt2px(wd)),
                int(self._pt2px(hg)),)

        self._draw_rectangle(
            self._pt2px(it.left),
            self._pt2px(it.top),
            self._pt2px(width),
            self._pt2px(height),
            it.style
            )

        if resize is not None:
            img = EmbeddedImage.get_pil_image_from_base64(data)
            pil_img = img.resize(resize)
        else:
            pil_img = EmbeddedImage.get_pil_image_from_base64(data)
        image = ImageTk.PhotoImage(pil_img)

        self._canvas.create_image(
            self._pt2px(it.left),
            self._pt2px(it.top),
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

    def _pt2px(self, val):
        return Size.convert_to_pixel(val, 'pt', self._ppi)

    def _px2pt(self, val):
        return Size.convert_from_pixel(val, 'pt', self._ppi)

    def help(self):
        'Tk canvas Render help'
