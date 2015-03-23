# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
import datetime
from xml.dom import minidom
from . page import Page
from . data import DataSourceObject, DataSetObject
from . style import Style
from .. import logger

class Report(object):
    def __init__(self):            
        self.report_def = None
        self.page=None
        self.parameters={}
        self.data_sources={}
        self.data_sets={}
        self.data_groups={}
        self.globals={}
        self.report_items_group={}
        self.current_scope=None
        self.style = Style(self)
        
    def parse_definition(self, report_def):
        self.report_def = report_def
        
    def parse_report(self, report_file):
        # 5.- Build pages
        logger.info('Building Page...')
        self.page = Page(self)

    def run(self, parameters={}):
        if not self.report_def:
            logger.critical("No ReportDef found. Run parse_definition() first.", True)
    
        self.globals={}
        if self.report_def.globals: # report_file, report_folder, report_name
            for key, value in self.report_def.globals.items():
                self.globals[key] = value       
        self.globals['page_number'] = -1
        self.globals['total_pages'] = -1
        self.globals['execution_time'] = datetime.datetime.now()
        logger.info('Execution time: {0}'.format(self.globals['execution_time']))

        # 1.- Resolve parameters values in declared order and log ivalid ones.
        self.parameters = {}
        for p in self.report_def.parameters_def:
            key=p.parameter_name
            if key in self.parameters:
                logger.error("ReportParameter '{0}' already assigned.".format(key), True)
            if key in parameters:
                self.parameters[key] = p.get_value(self, parameters[key])
            else:
                self.parameters[key] = p.get_default_value(self)
        if parameters:
            for key, value in parameters.items():
                if not key in self.report_def.parameters_def:
                    logger.warn("Unknown Parameter '{0}'. Ignored.".format(key))

        # 2.- Build data_sources
        logger.info('Running DataSources...')
        self.data_sources={}
        for ds in self.report_def.data_sources:
            self.data_sources[ds.name] = DataSourceObject(self, ds)
            self.data_sources[ds.name].connect()

        # 3.- Build data_sets
        logger.info('Running DataSets...')
        self.data_sets={}
        self.data_groups={}
        for ds in self.report_def.data_sets:
            logger.info("  Running DataSet '{0}'".format(ds.name))
            self.data_sets[ds.name] = DataSetObject(self, ds)
            self.data_sets[ds.name].execute()
            self.data_groups[ds.name] = self.data_sets[ds.name].data

        # 5.- Build pages
        logger.info('Building Page...')
        self.page = Page(self)
        

    def save(self, overwrite):
        '''
        Save report to nuntiare file
        '''

        def _add_element(doc, parent, element_name, text=None):
            el = doc.createElement(element_name)
            if text !=None:
                text_el = doc.createTextNode(text)
                el.appendChild(text_el)
            parent.appendChild(el)
            return el

        def _add_style(doc, styles_el, style):    
            st = _add_element(doc, styles_el, "Style")
            _add_element(doc, st, "Id", str(style.id))
            
            bd = _add_element(doc, st, "Border")
            if style.border:
                b = _add_element(doc, bd, "Top")
                _add_element(doc, b, "BorderStyle", style.border.style.top.value)
                _add_element(doc, b, "Color", style.border.color.top.value)
                _add_element(doc, b, "Width", str(style.border.width.top.value))
                b = _add_element(doc, bd, "Bottom")
                _add_element(doc, b, "BorderStyle", style.border.style.bottom.value)
                _add_element(doc, b, "Color", style.border.color.bottom.value)
                _add_element(doc, b, "Width", str(style.border.width.bottom.value))
                b = _add_element(doc, bd, "Left")
                _add_element(doc, b, "BorderStyle", style.border.style.left.value)
                _add_element(doc, b, "Color", style.border.color.left.value)
                _add_element(doc, b, "Width", str(style.border.width.left.value))
                b = _add_element(doc, bd, "Right")
                _add_element(doc, b, "BorderStyle", style.border.style.right.value)
                _add_element(doc, b, "Color", style.border.color.right.value)
                _add_element(doc, b, "Width", str(style.border.width.right.value))
                        
            if style.background_color:
                _add_element(doc, st, "BackgroundColor", style.background_color.value)

            if style.text:
                t = _add_element(doc, st, "Text")
                _add_element(doc, t, "FontFamily", style.text.font_family)
                _add_element(doc, t, "FontStyle", style.text.font_style)
                _add_element(doc, t, "FontSize", str(style.text.font_size))
                _add_element(doc, t, "FontWeight", str(style.text.font_weight))
                if style.text.format:
                    _add_element(doc, t, "Format", style.text.format)
                _add_element(doc, t, "TextDecoration", style.text.text_decoration)
                _add_element(doc, t, "TextAlign", style.text.text_align)
                _add_element(doc, t, "VerticalAlign", style.text.vertical_align)
                _add_element(doc, t, "Color", style.text.color)
                _add_element(doc, t, "PaddingTop", str(style.text.padding_top))
                _add_element(doc, t, "PaddingBottom", str(style.text.padding_bottom))
                _add_element(doc, t, "PaddingLeft", str(style.text.padding_left))
                _add_element(doc, t, "PaddingRight", str(style.text.padding_right))
                                
        def _add_header_footer(doc, parent, page_member, member_name):
            if not page_member:
                return
            el = _add_element(doc, parent, member_name)
            _add_element(doc, el, "Height", str(page_member.height))
            _add_element(doc, el, "PrintOnFirstPage", 
                    str(page_member.print_on_first_page))
            _add_element(doc, el, "PrintOnLastPage", 
                    str(page_member.print_on_last_page))
            if page_member.style:
                _add_element(doc, el, "StyleId", str(page_member.style.id))
            _add_report_items_definition(doc, el, page_member.definition)                

        def _add_report_items_definition(doc, parent, definition):
            items = definition.get_element("ReportItems")
            if not items:
                return
            items_el = _add_element(doc, parent, "ReportItems")            
            for it in items.reportitems_list:
                _add_literal(doc, items_el, it) # Works recursively

        def _add_literal(doc, parent, definition):
            if not definition:
                return
            l_parent = _add_element(doc, parent, definition.element_name)        
            for key, ex in definition.expression_list.items():
                _add_element(doc, l_parent, key, ex.expression)
            for key, ex in definition.non_expression_list.items():
                _add_literal(doc, l_parent, ex)
                
        def _add_report_items(doc, parent, body_items):
            if not body_items or not body_items.item_list:
                return
            pit = _add_element(doc, parent, "PageItems")
            for it in body_items.item_list:
                it_type = _add_element(doc, pit, it.type)
                _add_element(doc, it_type, "Name", it.name)
                _add_element(doc, it_type, "Top", str(it.top))
                _add_element(doc, it_type, "Left", str(it.left))
                _add_element(doc, it_type, "Height", str(it.height))
                _add_element(doc, it_type, "Width", str(it.width))
                if it.style:
                    st = _add_element(doc, it_type, "Style")
                    _add_element(doc, st, "StyleId", str(it.style.id))
                    
                if it.type=="PageText":
                    _add_element(doc, it_type, "Value", it.value_formatted)
                    _add_element(doc, it_type, "CanGrow", str(it.can_grow))
                    _add_element(doc, it_type, "CanShrink", str(it.can_shrink))
                
                if it.items_info:
                    _add_report_items(doc, it_type, it.items_info)
                    

        result_file = os.path.join(self.globals['output_directory'], 
                self.globals['output_name'] + ".nuntiare")
                
        if not overwrite:
            if os.path.isfile(result_file):
                logger.error("File '{0}' already exists.".format(result_file),
                        True, "IOError")

        doc = minidom.Document()
        root_element = doc.createElement("Nuntiare")

        gb = _add_element(doc, root_element, "Globals")
        for key, g in self.globals.items():
            if g:
                _add_element(doc, gb, key, str(g))
            else:
                _add_element(doc, gb, key)

        parameters = _add_element(doc, root_element, "Parameters")
        for key, p in self.parameters:
            pe = _add_element(doc, paraameters, "Parameter")
            _add_element(doc, pe, "Value", str(p))

        styles = _add_element(doc, root_element, "Styles")
        for key, st in self.style.styles.items():
            _add_style(doc, styles, st)

        page = _add_element(doc, root_element, "Page")
        _add_element(doc, page, "Height", str(self.page.height))
        _add_element(doc, page, "Width", str(self.page.width))
        _add_element(doc, page, "TopMargin", str(self.page.margin_top))
        _add_element(doc, page, "BottomMargin", str(self.page.margin_bottom))
        _add_element(doc, page, "LeftMargin", str(self.page.margin_left))
        _add_element(doc, page, "RightMargin", str(self.page.margin_right))
        _add_element(doc, page, "Columns", str(self.page.columns))
        _add_element(doc, page, "ColumnSpacing", str(self.page.column_spacing))
        _add_element(doc, page, "StyleId", str(self.page.style.id))

        _add_header_footer(doc, page, self.page.header, "PageHeader")
        _add_header_footer(doc, page, self.page.footer, "PageFooter")        
        
        body = _add_element(doc, root_element, "Body")
        if self.page.body.style:
            _add_element(doc, page, "StyleId", str(self.page.body.style.id))
        _add_report_items(doc, body, self.page.body.items)
        
        doc.appendChild(root_element)
        
        f = open(result_file, "wb")
        try:
            f.write(doc.toprettyxml(indent="  ", encoding="utf-8"))
        finally:
            f.close()
        
        logger.info("Report '{0}' saved.".format(result_file))
        
