# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. import logger
from ..tools import get_xml_tag_value 
from color import Color
from size import Size
from string import String
from integer import Integer
from boolean import Boolean
from variant import Variant
from data_type import DataType
from style.style import Style
from style.font import FontStyle, FontWeight, TextDecoration, \
    TextAlign, VerticalAlign, TextDirection, WritingMode
from style.border import BorderColor, BorderWidth, BorderStyle, BorderStyleEnum
from style.background import BackgroudImage, BackgroundRepeat, BackgroundGradientType
from report_parameter import ReportParameters, ReportParameter
from header_footer import PageHeader, PageFooter
from data_source import DataSources, DataSource, ConnectionProperties
from data_set import DataSets, DataSet, Fields, Field, Query, QueryParameters, QueryParameter
from body import Body
from report_items.report_item import ReportItems, Line, Rectangle, Textbox, Image
from report_items.grid import Grid, Columns, Column, Rows, Row, Cells, Cell
from report_items.image import ImageSourceEnum, ImageSizingEnum
from link import Link
from report_items.data_region.table import Table

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
    elif name=='Textbox':
        obj = Textbox(node, ln)
    elif name=='Image':
        obj = Image(node, ln)
    elif name=='Grid':
        obj = Grid(node, ln)
    elif name=='Columns':
        obj = Columns(node, ln)
    elif name=='Column':
        obj = Column(node, ln)
    elif name=='Rows':
        obj = Rows(node, ln)
    elif name=='Row':
        obj = Row(node, ln)
    elif name=='Cells':
        obj = Cells(node, ln)
    elif name=='Cell':
        obj = Cell(node, ln)
    elif name=='DataSources':
        obj = DataSources(node, ln)
    elif name=='DataSource':
        obj = DataSource(node, ln)
    elif name=='ConnectionProperties':
        obj = ConnectionProperties(node, ln)
    elif name=='DataSets':
        obj = DataSet(node, ln)
    elif name=='DataSets':
        obj = DataSet(node, ln)
    elif name=='Fields':
        obj = Fields(node, ln)
    elif name=='Field':
        obj = Field(node, ln)
    elif name=='Query':
        obj = Query(node, ln)
    elif name=='QueryParameters':
        obj = QueryParameters(node, ln)
    elif name=='QueryParameter':
        obj = QueryParameter(node, ln)
    elif name=='Table':
        obj = Table(node, ln)
    else:
        finish_critical("Unknown Element: '{0}'".format(name)) 

    return obj


def get_expression(name, node, report):
    value = get_xml_tag_value(node)

    # We need to use integer value avoiding circular reference with element module

    if name==0: # Element.NAME
        return None
    if name==2: # Element.STRING
        return String(report, value)
    if name==3: # Element.INTEGER
        return Integer(report, value)
    if name==4: # Element.BOOLEAN
        return Boolean(report, value)
    if name==5: # Element.SIZE
        return Size(report, value)
    if name==6: # Element.COLOR
        return Color(report, value)
    if name==8: # Element.URL
        return None
    if name==10: # Element.LANGUAGE
        return None
    if name==11: # Element.VARIANT
        return Variant(report, value)

    finish_critical("Unknown expression element definition: '{0}'".format(name))


def get_enum(name, node, report):

    value = get_xml_tag_value(node)
 
    if name=='BorderStyle':
        return BorderStyleEnum(report, value)
    if name=='FontStyle':
        return FontStyle(report, value)
    if name=='FontWeight':
        return FontWeight(report, value)
    if name=='TextDecoration':
        return TextDecoration(report, value)
    if name=='TextAlign':
        return TextAlign(report, value)
    if name=='VerticalAlign':
        return VerticalAlign(report, value)
    if name=='TextDirection':
        return TextDirection(report, value)
    if name=='WritingMode':
        return WritingMode(report, value)
    if name=='ImageSource':
        return ImageSourceEnum(report, value)
    if name=='ImageSizing':
        return ImageSizingEnum(report, value)
    if name=='BackgroundRepeat':
        return BackgroundRepeat(report, value)
    if name=='BackgroundGradientType':
        return BackgroundGradientType(report, value)
    if name=='DataType':
        return DataType(report, value)

    finish_critical("Unknown Enum: '{0}'".format(name))


def finish_critical(error):
    logger.critical(error)
    raise ValueError(error)

