# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import os
import datetime
from xml.dom import minidom
from . parser import Parser
from . result import Result
from . import logger

class Report(object):
    def __init__(self, definition, 
            output_name=None, output_directory=None):

        super(Report, self).__init__()

        self.parser = None
        self.result = None
        self.parameters = {}
        self.data_sources = {}
        self.data_sets = {}
        self.data_groups = {}
        self.globals = {}
        self.report_items_group = {}
        self.current_scope = None
        
        self._parse(definition, output_name, output_directory)
        self.parser.style.get_style(None)
        
    def _parse(self, definition, output_name, output_directory):
        '''
        Parse the definition for this report.
        definition can be a xml definition file, 
        a nuntiare report file or a simple xml string.
        Run() must be executed in order to get the report.
        '''

        if not definition:
            logger.critical("Error in definition '{0}'. " \
                "definition must be a xml definition file, " \
                "a simple xml string or a nuntiare report file.".format(definition), True)
                
        self.parser = Parser(self, definition, output_name, output_directory).parser        
        
    def run(self, parameters={}):
        if not self.parser:
            logger.critical("No definition found in report.", True)            
    
        self.globals = self.parser.get_globals()
        self.globals['page_number'] = -1
        self.globals['total_pages'] = -1
        self.globals['execution_time'] = datetime.datetime.now()
        if not self.globals['output_name']:
            self.globals['output_name'] = self.globals['report_name']
        logger.info('Execution time: {0}'.format(self.globals['execution_time']))

        logger.info('Running Parameters...')
        self.parser.get_parameters(parameters)

        logger.info('Running DataSources...')
        self.data_sources = self.parser.get_data_sources()

        logger.info('Running DataSets...')
        self.data_sets, self.data_groups = self.parser.get_data_sets()

        logger.info('Building result...')
        self.result = Result(self)

    def save(self, overwrite):
        '''
        Save report to nuntiare file
        '''

        def _add_element(doc, parent, element_name, text=None, cdata=None):
            if cdata: 
                el = doc.createCDATASection(cdata)
            else:
                el = doc.createElement(element_name)
            if text !=None:
                text_el = doc.createTextNode(text)
                el.appendChild(text_el)
            parent.appendChild(el)
            return el

        def _add_style(doc, styles_el, style):    
            st = _add_element(doc, styles_el, "Style")
            _add_element(doc, st, "Id", str(style.id))
            
            _add_style_border(doc, st, style.top_border, "TopBorder")
            _add_style_border(doc, st, style.bottom_border, "BottomBorder")
            _add_style_border(doc, st, style.left_border, "LeftBorder")
            _add_style_border(doc, st, style.right_border, "RightBorder")
                        
            if style.background_color:
                _add_element(doc, st, "BackgroundColor", style.background_color)

            _add_element(doc, st, "FontFamily", style.font_family)
            _add_element(doc, st, "FontStyle", style.font_style)
            _add_element(doc, st, "FontSize", str(style.font_size))
            _add_element(doc, st, "FontWeight", str(style.font_weight))
            if style.format:
                _add_element(doc, st, "Format", style.format)
            _add_element(doc, st, "TextDecoration", style.text_decoration)
            _add_element(doc, st, "TextAlign", style.text_align)
            _add_element(doc, st, "VerticalAlign", style.vertical_align)
            _add_element(doc, st, "Color", style.color)
            _add_element(doc, st, "PaddingTop", str(style.padding_top))
            _add_element(doc, st, "PaddingBottom", str(style.padding_bottom))
            _add_element(doc, st, "PaddingLeft", str(style.padding_left))
            _add_element(doc, st, "PaddingRight", str(style.padding_right))

        def _add_style_border(doc, parent, border_def, border_name):
            bd = _add_element(doc, parent, border_name)            
            if border_def:
                _add_element(doc, bd, "Color", border_def.color)
                _add_element(doc, bd, "BorderStyle", border_def.border_style)
                _add_element(doc, bd, "Width", str(border_def.width))
                                
        def _add_header_footer(doc, parent, page_member, member_name):
            if not page_member:
                return
            _add_literal(doc, parent, page_member.definition)

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
                _add_element(doc, it_type, "Type", it.report_item_def.element_name)
                _add_element(doc, it_type, "Name", it.name)
                _add_element(doc, it_type, "Top", str(it.top))
                _add_element(doc, it_type, "Left", str(it.left))
                _add_element(doc, it_type, "Height", str(it.height))
                _add_element(doc, it_type, "Width", str(it.width))
                if it.style:
                    _add_element(doc, it_type, "StyleId", str(it.style.id))
                    
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

        parameters = _add_element(doc, root_element, "ReportParameters")
        for key, p in self.parameters.items():
            pe = _add_element(doc, parameters, "ReportParameter")
            _add_element(doc, pe, "Name", key)
            para_def = self.parser.object.get_parameter_def(key)
            if para_def.data_type:
                _add_element(doc, pe, "DataType", para_def.data_type)
            if p == None:
                _add_element(doc, pe, "Value")
            else:        
                _add_element(doc, pe, "Value", str(p))

        styles = _add_element(doc, root_element, "Styles")
        for key, st in self.parser.style.styles.items():
            _add_style(doc, styles, st)

        page = _add_element(doc, root_element, "Page")
        _add_element(doc, page, "PageHeight", str(self.result.height))
        _add_element(doc, page, "PageWidth", str(self.result.width))
        _add_element(doc, page, "TopMargin", str(self.result.margin_top))
        _add_element(doc, page, "BottomMargin", str(self.result.margin_bottom))
        _add_element(doc, page, "LeftMargin", str(self.result.margin_left))
        _add_element(doc, page, "RightMargin", str(self.result.margin_right))
        _add_element(doc, page, "Columns", str(self.result.columns))
        _add_element(doc, page, "ColumnSpacing", str(self.result.column_spacing))
        if self.result.style:
            _add_element(doc, page, "StyleId", str(self.result.style.id))

        _add_header_footer(doc, page, self.result.header, "PageHeader")
        _add_header_footer(doc, page, self.result.footer, "PageFooter")        
        
        body = _add_element(doc, root_element, "Body")
        if self.result.body.style:
            _add_element(doc, body, "StyleId", str(self.result.body.style.id))
        _add_report_items(doc, body, self.result.body.items)
        
        doc.appendChild(root_element)
        
        f = open(result_file, "wb")
        try:
            f.write(doc.toprettyxml(indent="  ", encoding="utf-8"))
        finally:
            f.close()
        
        logger.info("Report '{0}' saved.".format(result_file))

