# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . import logger, __pixels_per_inch__
import xml.parsers.expat

size_6 = float(6)
size_10 = float(10)
size_25_4 = float(25.4)
size_72 = float(72)

def get_xml_tag_value(node):
    'Returns the valid value of xml node'
    xml_str = node.toxml() 
    start = xml_str.find('>')
    if start == -1:
        return ''
    end = xml_str.rfind('<')
    if end < start:
        return ''
    res = unescape(xml_str[start + 1:end])
    print "res: " + res
    return res

def unescape(s):
    want_unicode = False
    if isinstance(s, unicode):
        s = s.encode("utf-8")
        want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    list = []
   
    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append
   
    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s, 0)
    p.Parse("</e>", 1)
   
    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(list)


def get_parameters_from_string(string):
    '''
    Process a string with filename and parameters 
    in a format of file.xml?param1=value1+param2=value2+paramn=valuen
    and returns a dictionary with the information:
        result['file'] --> xml report definition file
        result['parameters'] --> a dictionary with parameters information
            result['param_1_name'] --> returns a param_1 value
            result['param_2_name'] --> returns a param_2 value
            result['param_n_name'] --> returns a param_n value
    '''
    result={}
    parameters={}

    filename=string

    i=string.find('?')
    if i > -1:
        filename=string[:i].strip()
        para_str=string[i+1:]
        ps = para_str.split('+')
        for p in ps:
            i_eq=p.find('=')
            if i_eq<1:
                logger.warn("Parameter in wrong format: {0}. Continue with next parameter.".format(p))
                continue
            name = p[:i_eq]
            val = p[i_eq+1:]
            parameters[name]= val

    result['file']=filename
    result['parameters']=parameters

    return result


def raise_error_with_log(message, error_type=None):
    logger.error(message)
    if not error_type or error_type=='ValueError':
        raise ValueError(message)
    raise ValueError(message)


def get_element_from_parent(parent_element, child_name):
    '''
    Returns a child element definition from parent element
    '''
    if parent_element:
        return parent_element.get_element(child_name)


def get_expression_value_or_default(element, child_name, default_value, direct_expression=None):
    '''
    Gets the value of a report element of type expression, or its default value 
    '''
    if direct_expression != None: # child_name is the expression to get value
        value = direct_expression.value()
        if value == None:
            return default_value
        return value

    el = get_element_from_parent(element, child_name) 
    if not el:
        return default_value
    value = el.value()
    if value == None:
        return default_value
    return value


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
    if unit=='mm':
        return size

    if unit=="in":
        return size / size_25_4
    elif unit=="cm":
        return size / size_10
    elif unit=="pt":
        return int((size / size_25_4) * size_72)
    elif unit=="pc":
        return int((size / size_25_4) * size_6)
    elif unit=="dot" or 'px':
        return int((size * __pixels_per_inch__) / size_25_4)

    raise_error_with_log("Unknown unit '{0}'".format(unit))

def get_float_rgba(c):
    return float(c) / float(65535) 

