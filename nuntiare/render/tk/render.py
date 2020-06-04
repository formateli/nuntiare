# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from PIL import ImageTk
from nuntiare.definition.expression import Size
from nuntiare.definition.element import EmbeddedImage
from .. render import Render
from ... import LOGGER


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

        i = 0
        for it in items:
            if it.type == 'PageImage':
                i += 1
                self._draw_image(it)
                if i == 4:
                    break  # TODO just one for the moment
            else:
                continue

    def _draw_image(self, it):
        width = it.width
        height = it.height

        if it.image_source == 'Embedded':
            el = it.report.definition.EmbeddedImages
            imgem = el.embedded_images[it.image_value]
            data = imgem.ImageData
        elif it.image_source == 'External':
            data = EmbeddedImage.get_base64_image(
                it.image_value, it.name, it.mimetype)[2]

        resize = None

        if it.image_sizing == 'AutoSize':
            width = Size.convert_from_pixel(
                    imgem.image_width, 'pt', self._ppi)
            height = Size.convert_from_pixel(
                    imgem.image_height, 'pt', self._ppi)
        elif it.image_sizing == 'Fit':
            resize = (int(Size.convert_to_pixel(width, 'pt', self._ppi)),
                      int(Size.convert_to_pixel(height, 'pt', self._ppi)))
        elif it.image_sizing == 'FitProportional':
            wd, hg = EmbeddedImage.get_proportional_size(
                    it.width, it.height,
                    imgem.image_width,
                    imgem.image_height)
            resize = (int(wd), int(hg))

        self._draw_rectangle(
            Size.convert_to_pixel(it.left, 'pt', self._ppi),
            Size.convert_to_pixel(it.top, 'pt', self._ppi),
            Size.convert_to_pixel(width, 'pt', self._ppi),
            Size.convert_to_pixel(height, 'pt', self._ppi),
            it.style
            )

        if resize is not None:
            img = EmbeddedImage.get_pil_image_from_base64(data)
            pil_img = img.resize(resize)
        else:
            pil_img = EmbeddedImage.get_pil_image_from_base64(data)
        image = ImageTk.PhotoImage(pil_img)

        self._canvas.create_image(
            Size.convert_to_pixel(it.left, 'pt', self._ppi),
            Size.convert_to_pixel(it.top, 'pt', self._ppi),
            image=image,
            anchor='nw',
            )

        if not image in self._images:
            self._images.append(image)

    def _draw_rectangle(self, left, top, width, height, style):
        self._canvas.create_rectangle(
                left, top,
                left + width, top + height,
                fill=style.background_color)

    def help(self):
        'Tk canvas Render help'
