# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import os
from tkinter import PhotoImage


class ImageManager():
    def __init__(self):
        self._images = {}

    def add_images(self, image_list):
        for image in image_list:
            self.add_image(image)

    def add_image(self, image_file):
        if not os.path.isfile(image_file):
            raise Exception(
                "Image file '{0}' not found.".format(image_file))
        if not os.access(image_file, os.R_OK):
            raise Exception(
                "User has not read access for '{0}'.".format(image_file))

        name = os.path.splitext(
            os.path.basename(image_file))[0]
        if name in self._images:
            raise Exception("Image '{0}' already exists.".format(name))
        image = PhotoImage(file=image_file)
        self._images[name] = image
        
    def get_image(self, name):
        if name not in self._images:
            raise Exception("Image '{0}' not found.".format(name))
        return self._images[name]
