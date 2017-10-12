# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . import logger, __pixels_per_inch__
from xml.parsers import expat


size_6 = float(6)
size_10 = float(10)
size_25_4 = float(25.4)
size_72 = float(72)


def get_xml_tag_value(node):
    'Returns the valid value of xml node'
    xml_str = node.toxml()
    start = xml_str.find('>')
    if start == -1:
        return
    end = xml_str.rfind('<')
    if end < start:
        return
    res = unescape(xml_str[start + 1:end])
    return res


def unescape(s):
    # want_unicode = False
    if not isinstance(s, str):
        s = s.encode("utf-8")
    # if isinstance(s, unicode):
    #     s = s.encode("utf-8")
    #     want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    list = []

    # create and initialize a parser object
    p = expat.ParserCreate("utf-8")
    p.buffer_text = True
    # p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append

    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s, 0)
    p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    # if want_unicode:
    #     es = u""
    return es.join(list)


def inch_2_mm(inch):
    '''
    Converts inches to millimeters
    '''
    return float(inch * 25.4)


def dot_2_mm(dots, pixels_per_inch=__pixels_per_inch__):
    return (dots * size_25_4) / pixels_per_inch


def point_2_mm(points):
    return float((points * size_25_4) / size_72)


def get_size_in_unit(size, unit):
    unit = unit.strip().lower()
    if unit == 'mm':
        return size

    if unit == "in":
        return size / size_25_4
    elif unit == "cm":
        return size / size_10
    elif unit == "pt":
        return int((size / size_25_4) * size_72)
    elif unit == "pc":
        return int((size / size_25_4) * size_6)
    elif unit == "dot" or 'px':
        return int((size * __pixels_per_inch__) / size_25_4)

    raise_error_with_log("Unknown unit '{0}'".format(unit))


def get_float_rgba(c):
    return float(c) / float(65535)
