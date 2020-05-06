# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import os, io
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from wand.api import library
import wand.color
import wand.image


def _get_curr_directory():
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, 'images')
    return path


class ImageManager:

    _images = {}
    _paths = [_get_curr_directory()]

    @classmethod
    def get_image(cls, name, size=None,
                color=None, extension='svg'):
        image = cls._get_image(name, size, color)
        if image is None:
            image = cls._create_image(name, size, color, extension)
        return image

    @classmethod
    def add_image_path(cls, path):
        if path in cls._paths:
            return
        if not os.path.exists(path):
            raise Exception(
                "Image path '{}' not found.".format(path))
        cls._paths.append(path)

    @classmethod
    def _create_image(cls, name, size, color, extension):
        def get_source(path):
            s = os.path.join(path, extension, name + '.' + extension)
            if not os.path.exists(s):
                return
            return s

        source = None
        for path in cls._paths:
            source = get_source(path)
            if source is not None:
                break
        if source is None:
            raise Exception(
                "Image '{}' not found.".format(name))

        if extension == 'svg':
            data = cls._svg2png(source, color)
            image = Image.open(data)
        else:
            image = Image.open(source)

        if size is not None:
            width, height = size.split('x')
            image = image.resize((int(width), int(height)))

        photo = ImageTk.PhotoImage(image)
        cls._add_image(photo, name, size, color)
        return photo

    @classmethod
    def _svg2png(cls, source, color):
        if color is not None:
            try:
                with open(source, 'rb') as fp:
                    data = fp.read()
                ET.register_namespace('', 'http://www.w3.org/2000/svg')
                root = ET.fromstring(data)
                root.attrib['fill'] = color
                data_svg = io.BytesIO(ET.tostring(root))
            except ET.ParseError:
                pass
        else:
            with open(source, 'rb') as f:
                data_svg = io.BytesIO(f.read())

        with wand.image.Image() as image:
            with wand.color.Color('transparent') as background_color:
                library.MagickSetBackgroundColor(image.wand,
                                                 background_color.resource)
            image.read(blob=data_svg.read())
            png_image = image.make_blob('png32')

        data = io.BytesIO()
        data.write(png_image)
        return data

    @classmethod
    def _get_image(cls, name, size, color):
        if name not in cls._images:
            return
        if size not in cls._images[name]:
            return
        if color not in cls._images[name][size]:
            return
        return cls._images[name][size][color]

    @classmethod
    def _add_image(cls, image, name, size, color):
        if name not in cls._images:
            cls._images[name] = {}
        if size not in cls._images[name]:
            cls._images[name][size] = {}
        if color not in cls._images[name][size]:
            cls._images[name][size][color] = image
