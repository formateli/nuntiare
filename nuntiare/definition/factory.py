# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare import logger
from nuntiare.tools import get_xml_tag_value 
from color import Color
from size import Size
from string import String
from integer import Integer
from boolean import Boolean
from data_type import DataType
from style.style import Style
from style.font import FontStyle, FontWeight, TextDecoration, TextAlign, VerticalAlign, TextDirection, WritingMode
from style.border import BorderColor, BorderWidth, BorderStyle, BorderStyleEnum
from style.background import BackgroudImage, BackgroundRepeat, BackgroundGradientType
from report_parameter import ReportParameters, ReportParameter, ValidValues, DataSetReference, ParameterValues, ParameterValue, DefaultValue, Values
from header_footer import PageHeader, PageFooter
from body import Body
from report_items.report_item import ReportItems
from report_items.line import Line
from report_items.rectangle import Rectangle
from report_items.image import Image, ImageSourceEnum, ImageSizingEnum
from link import Link

def get_element(name, node, lnk):
    ln = Link(lnk.report, lnk.obj)
    if name=='PageHeader':
        obj = PageHeader(node, ln)
    elif name=='PageFooter':
        obj = PageFooter(node, ln)
    elif name=='Body':
        obj = Body(node, ln)
    elif name=='ReportParameters':
        obj = ReportParameters(node, ln)
    elif name=='ReportParameter':
        obj = ReportParameter(node, ln)
    elif name=='ValidValues':
        obj = ValidValues(node, ln)
    elif name=='DataSetReference':
        obj = DataSetReference(node, ln)
    elif name=='ParameterValues':
        obj = ParameterValues(node, ln)
    elif name=='ParameterValue':
        obj = ParameterValue(node, ln)
    elif name=='DefaultValue':
        obj = DefaultValue(node, ln)
    elif name=='Values':
        obj = Values(node, ln)
    elif name=='BorderColor':
        obj = BorderColor(node, ln)
    elif name=='BorderWidth':
        obj = BorderWidth(node, ln)
    elif name=='BorderStyle':
        obj = BorderStyle(node, ln)
    elif name=='Style':
        obj = Style(node, ln)
    elif name=='BackgroudImage':
        obj = BackgroudImage(node, ln)
    elif name=='ReportItems':
        obj = ReportItems(node, ln)
    elif name=='Line':
        obj = Line(node, ln)
    elif name=='Rectangle':
        obj = Rectangle(node, ln)
    elif name=='Image':
        obj = Image(node, ln)
    else:
        finish_critical("Unknown Element: '{0}'".format(name)) 
    
    obj.lnk.obj=obj
    return obj

def get_expression(name, node):
    value = get_xml_tag_value(node)

    # We need to use integer value avoiding circular reference with element module

    if name==0: # Element.NAME
        return None
    if name==2: # Element.STRING
        return String(value)
    if name==3: # Element.INTEGER
        return Integer(value)
    if name==4: # Element.BOOLEAN
        return Boolean(value)
    if name==5: # Element.SIZE
        return Size(value)
    if name==6: # Element.COLOR
        return Color(value)
    if name==8: # Element.URL
        return None
    if name==10: # Element.LANGUAGE
        return None

    finish_critical("Unknown Expression: '" + str(name) + "'") 


def get_enum(name, node):

    value = get_xml_tag_value(node)

    if name=='BorderStyle':
        return BorderStyleEnum(value)
    if name=='FontStyle':
        return FontStyle(value)
    if name=='FontWeight':
        return FontWeight(value)
    if name=='TextDecoration':
        return TextDecoration(value)
    if name=='TextAlign':
        return TextAlign(value)
    if name=='VerticalAlign':
        return VerticalAlign(value)
    if name=='TextDirection':
        return TextDirection(value)
    if name=='WritingMode':
        return WritingMode(value)
    if name=='ImageSource':
        return ImageSourceEnum(value)
    if name=='ImageSizing':
        return ImageSizingEnum(value)
    if name=='BackgroundRepeat':
        return BackgroundRepeat(value)
    if name=='BackgroundGradientType':
        return BackgroundGradientType(value)
    if name=='DataType':
        return DataType(value)

    finish_critical("Unknown Enum: '" + name + "'")

def finish_critical(error):
    logger.critical(error)
    raise ValueError(error)



