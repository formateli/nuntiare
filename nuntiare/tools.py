# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare import logger

def get_xml_tag_value(node):
    'Returns the valid value of node'
    xml_str = node.toxml() 
    start = xml_str.find('>')
    if start == -1:
        return ''
    end = xml_str.rfind('<')
    if end < start:
        return ''
    return xml_str[start + 1:end]

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




