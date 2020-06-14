# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from nuntiare.definition.expression import Size


def get_size_px(value):
    res = Size.split_size_string(value)
    if res is None:
        return
    return int(Size.convert_to_pixel(float(res[0]), res[1]))
