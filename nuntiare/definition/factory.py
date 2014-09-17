# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. import logger
from ..tools import get_xml_tag_value 
from link import Link
from page import Page
from report_parameter import ReportParameters, ReportParameter

from data.data_type import DataType
from data.data_source import DataSources, DataSource, ConnectionProperties
from data.data_set import DataSets, DataSet, Fields, Field, Query, \
        QueryParameters, QueryParameter
from data.sort import SortExpressions, SortExpression, SortDirection
from data.filter import Operator, Filters, Filter, FilterValues
from data.group import Group, GroupExpressions

from report_element.visibility import Visibility
from report_element.body import Body
from report_element.page_section import PageHeader, PageFooter
from report_element.report_item.report_item import ReportItems
from report_element.report_item.data_region.tablix import Tablix, TablixCorner, \
        TablixCornerRows, TablixCornerRow, TablixCornerCell, CellContents, \
        TablixColumnHierarchy, TablixRowHierarchy, TablixMembers, TablixMember, \
        TablixHeader, TablixBody, TablixColumns, TablixColumn, TablixRows, TablixRow, \
        TablixCells, TablixCell
        
#from module import Imports, Import
from types.color import Color
from types.size import Size
from types.string import String
from types.integer import Integer
from types.boolean import Boolean
from types.variant import Variant

from style.style import Style
from style.font import FontStyle, FontWeight, TextDecoration, \
        TextAlign, VerticalAlign, TextDirection, WritingMode
from style.border import Border, TopBorder, BottomBorder, LeftBorder, RightBorder, BorderStyleEnum
from style.background import BackgroundImage, BackgroundRepeat, BackgroundGradientType

#from report_element.report_item.line import Line
#from report_element.report_item.rectangle import Rectangle
#from report_element.report_item.textbox import Textbox

#from report_items.grid import Grid, Columns, Column, Rows, Row, Cells, Cell
#from report_items.image import Image, ImageSourceEnum, ImageSizingEnum
#from report_items.data_region.table import Table,  \
#    Header, Footer, Details, TableGroups, TableGroup


def get_element(name, node, lnk):
    ln = Link(lnk.report_def, lnk.obj)
    if name=='PageHeader':
        obj = PageHeader(node, ln)
    elif name=='PageFooter':
       obj = PageFooter(node, ln)
    elif name=='Body':
        obj = Body(node, ln)   
    elif name=='Visibility':
        obj = Visibility(node, ln)             
    elif name=='DataSources':
        obj = DataSources(node, ln)
    elif name=='DataSource':
        obj = DataSource(node, ln)
    elif name=='ConnectionProperties':
        obj = ConnectionProperties(node, ln)
    elif name=='DataSets':
        obj = DataSets(node, ln)
    elif name=='DataSet':
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
    elif name=='SortExpressions':
        obj = SortExpressions(node, ln)
    elif name=='SortExpression':
        obj = SortExpression(node, ln)
    elif name=='Filters':
        obj = Filters(node, ln)
    elif name=='Filter':
        obj = Filter(node, ln)
    elif name=='Group':
        obj = Group(node, ln)        
    elif name=='ReportParameters':
        obj = ReportParameters(node, ln)
    elif name=='ReportParameter':
        obj = ReportParameter(node, ln)
    elif name=='ReportItems':
        obj = ReportItems(node, ln)        
    elif name=='Tablix':
        obj = Tablix(node, ln)
    elif name=='TablixColumnHierarchy':
        obj = TablixColumnHierarchy(node, ln)
    elif name=='TablixRowHierarchy':
        obj = TablixRowHierarchy(node, ln)
    elif name=='TablixMembers':
        obj = TablixMembers(node, ln)
    elif name=='TablixMember':
        obj = TablixMember(node, ln)
    elif name=='TablixBody':
        obj = TablixBody(node, ln)
    elif name=='TablixColumns':
        obj = TablixColumns(node, ln)
    elif name=='TablixColumn':
        obj = TablixColumn(node, ln)
    elif name=='TablixRows':
        obj = TablixRows(node, ln)
    elif name=='TablixRow':
        obj = TablixRow(node, ln)
    elif name=='TablixCells':
        obj = TablixCells(node, ln)
    elif name=='TablixCell':
        obj = TablixCell(node, ln)
    elif name=='CellContents':
        obj = CellContents(node, ln)        
    elif name=='Style':
        obj = Style(node, ln)
    elif name=='Border':
        obj = Border(node, ln)
    elif name=='TopBorder':
        obj = TopBorder(node, ln)
    elif name=='BottomBorder':
        obj = BottomBorder(node, ln)
    elif name=='LeftBorder':
        obj = LeftBorder(node, ln)
    elif name=='RightBorder':
        obj = RightBorder(node, ln)
    elif name=='BackgroundImage':
        obj = BackgroundImage(node, ln)
        
#    elif name=='Line':
#        obj = Line(node, ln)
#    elif name=='Rectangle':
#        obj = Rectangle(node, ln)
#    elif name=='Textbox':
#        obj = Textbox(node, ln)
#    elif name=='Image':
#        obj = Image(node, ln)
#    elif name=='Grid':
#        obj = Grid(node, ln)
#    elif name=='Columns':
#        obj = Columns(node, ln)
#    elif name=='Column':
#        obj = Column(node, ln)
#    elif name=='Rows':
#        obj = Rows(node, ln)
#    elif name=='Row':
#        obj = Row(node, ln)
#    elif name=='Cells':
#        obj = Cells(node, ln)
#    elif name=='Cell':
#        obj = Cell(node, ln)
        
#    elif name=='Table':
#        obj = Table(node, ln)
#    elif name=='Header':
#        obj = Header(node, ln)
#    elif name=='Footer':
#        obj = Footer(node, ln)
#    elif name=='Details':
#       obj = Details(node, ln)
#    elif name=='TableGroups':
#        obj = TableGroups(node, ln)
#    elif name=='TableGroup':
#        obj = TableGroup(node, ln)
        

#    elif name=='Imports':
#        obj = Imports(node, ln)
#    elif name=='Import':
#        obj = Import(node, ln)
    else:
        finish_critical("Unknown Element: '{0}'".format(name)) 

    return obj


def get_expression(name, node, must_be_constant=False):
    value = get_xml_tag_value(node)

    # We need to use integer value avoiding circular reference with element module

    if name==1: # Element.STRING
        return String(value, must_be_constant)
    if name==2: # Element.INTEGER
        return Integer(value, must_be_constant)
    if name==3: # Element.BOOLEAN
        return Boolean(value, must_be_constant)
    if name==5: # Element.SIZE
        return Size(value, must_be_constant)        
    if name==7: # Element.COLOR
        return Color(value, must_be_constant)
    if name==10: # Element.URL
        return None
    if name==90: # Element.VARIANT
        return Variant(value, must_be_constant)
 
    finish_critical("Unknown expression element definition: '{0}'. Node Name: '{1}'".format(name, node.nodeName))


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
    if name=='SortDirection':
        return SortDirection(value)
    if name=='Operator':
        return Operator(value)

    finish_critical("Unknown Enum: '{0}'. Node Name: '{1}'".format(name, node.nodeName))


def get_expression_list(name, node, lnk):
    ln = Link(lnk.report_def, lnk.obj)
    if name=='FilterValues':
        obj = FilterValues(node, ln)
    elif name=='GroupExpressions':
        obj = GroupExpressions(node, ln)
    else:
        finish_critical("Unknown Element: '{0}' for ExpressionList".format(name)) 

    return obj


def finish_critical(error):
    logger.critical(error)
    raise ValueError(error)

