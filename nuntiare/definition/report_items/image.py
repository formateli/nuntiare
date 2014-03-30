# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ...definition.enum import Enum

class ImageSourceEnum(Enum):
    enum_list={'external': 'External',
               'embedded': 'Embedded', 
               'database': 'Database', 
              }

    def __init__(self, expression):
        super(ImageSourceEnum, self).__init__('ImageSource', expression, ImageSourceEnum.enum_list)


class ImageSizingEnum(Enum):
    '''
    Defines the behavior if the image does not
    fit within the specified size.
    AutoSize = The borders should grow/shrink
      to accommodate the image (Default).
    Fit = The image is resized to exactly match
      the height and width of the image element.
    FitProportional = The image should be
      resized to fit, preserving aspect ratio
    Clip = The image should be clipped to fit
    '''

    enum_list={'autosize': 'AutoSize',
               'fit': 'Fit', 
               'fitproportional': 'FitProportional', 
               'clip': 'Clip', 
              }

    def __init__(self, expression):
        super(ImageSizingEnum, self).__init__('ImageSizing', expression, ImageSizingEnum.enum_list)


