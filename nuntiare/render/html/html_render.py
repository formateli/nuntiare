# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
import cgi
from .. render import Render
from ... tools import raise_error_with_log
from ... report.page_item.page_item import PageRectangle

class HtmlRender(Render):
    def __init__(self):
        super(HtmlRender, self).__init__(extension='html')
        self.doc = None
        self.style_helper = StyleHelper()

    def render(self, report):
        super(HtmlRender, self).render(report)

        report.globals['total_pages'] = 1
        report.globals['page_number'] = 1

        self.doc = HtmlElement("DOCTYPE", None)
        html = HtmlElement("html", None)
        head = self.get_head(report) 
        html.add_element(head)
        self.doc.add_element(html)

        body = HtmlElement("body", None)

        container = HtmlElement("div", "container")
        container.add_attribute("style", "width:{0}mm".format(report.pages.available_width))

        self.get_report_header_footer("header", report, report.pages.header, container)   
        self.get_report_body(report, container)
        self.get_report_header_footer("footer", report, report.pages.footer, container)

        body.add_element(container)
        html.add_element(body)

        str_style = "div#Middle {display: inline-block;vertical-align: middle;}\n" + \
                "div#Bottom {display: inline-block;vertical-align: bottom;}\n"
        for key, value in self.style_helper.style_list.items():
            if value.find("; vertical-align:Middle;") > -1:
                str_style = str_style + key + \
                    ":before {content: ''; display: inline-block;height: 100%; vertical-align: middle;margin-right: -0.1em;}\n"
            if value.find("; vertical-align:Bottom;") > -1:
                str_style = str_style + key + \
                    ":before {content: ''; display: inline-block;height: 100%; vertical-align: bottom;margin-right: -0.1em;}\n"
            str_style = str_style + key + "{" + value + "}\n"

        if str_style != "":
            style = HtmlElement("style", None)
            style.add_attribute("type", "text/css")
            style.add_element(HtmlElement("text", None, str_style))
            head.add_element(style)

        self.write_to_file()

    def get_head(self, report):
        head = HtmlElement("head", None)
        title = HtmlElement("title", None)
        title.add_element(HtmlElement("text", None, report.globals['report_name']))
        head.add_element(title)
        return head

    def get_report_header_footer(self, name, report, header_footer, container):
        if not header_footer: 
            return
        if not header_footer.definition:
            return
        rec = PageRectangle(report, header_footer.definition, None)
        rec.name = "div_" + name 
        rec.width = report.pages.available_width
        items = [rec,]
        report_header = HtmlElement("div", "{0}_container".format(name))
        if name == "header": 
            report_header.add_attribute("style", "height:{0}mm".format(header_footer.height)) 
        else:
            report_header.add_attribute("style", "clear:both; height:{0}mm".format(header_footer.height))
        container.add_element(report_header)
        self.render_items(items, report_header)

    def get_report_body(self, report, container):
        report_body = HtmlElement("div", "body_container")
        report_body.add_attribute("style", "float:left; padding:1mm 1mm 1mm 1mm; width:{0}mm".format(report.pages.available_width)) 
        container.add_element(report_body)
        items = report.pages.body_items.item_list
        self.render_items(items, report_body)

    def render_items(self, items, container):
        for it in items:
            if it.type == "PageLine" or it.type == "PageBreak":
                continue
            if it.type == "PageRectangle" or it.type == "PageText":
                el = self.get_rectangle(it)
            if it.type == "PageGrid" or it.type == "PageTable":
                el = self.get_grid(it)

            container.add_element(el)

    def get_grid(self, it):
        grid = HtmlElement("table", it.name)
        self.add_style(grid, it, ignore_list=['height',])

        for row in it.rows:
            if row.hidden:
                continue
            rw = HtmlElement("tr", None)
            for cell in row.cells:
                self.render_items(cell.items_info.item_list, rw)
            grid.add_element(rw)
        
        res = self.get_td_parent_element(it, grid)  
        return res

    def get_rectangle(self, it):
        is_textbox = True if it.type == "PageText" else False
        vertical_align = None
        in_cell = self.is_in_cell(it) 

        txt = ""
        if is_textbox:
            txt = it.value_formatted
            if txt:
                txt = cgi.escape(txt).encode('ascii', 'xmlcharrefreplace')
                txt = txt.replace("\n", "<br>") # New line                
            else:
                txt = ""

        if not is_textbox or not it.parent or it.parent.type == "PageRectangle":
            # It is just a rectangle or a Textbox belonging to a rectangle.
            is_div = True
        else: # It is a Textbox belonging to a cell.
            is_div = False

        if is_div:
            rec = HtmlElement("div", it.name)
            ignore = []
            if it.name == "div_header" or it.name == "div_footer":
                ignore = ['overflow',]
            if is_textbox and (it.can_grow or it.can_shrink):
                ignore.append('height')
            if it.style.text.vertical_align == "Middle" or it.style.text.vertical_align == "Bottom": 
                vertical_align = it.style.text.vertical_align
            self.add_style(rec, it, txt, ignore_list=ignore)
        else: 
            rec = HtmlElement("td", it.name)
            if it.parent.col_span > 1:
                rec.add_attribute("colspan", it.parent.col_span)
            it.width = it.parent.width
            self.add_style(rec, it, txt, ['height',])
 
        if txt != "" and not vertical_align:
            rec.add_element(HtmlElement("text", None, txt))

        self.render_items(it.get_item_list(), rec)

        if is_div and in_cell:
            res = self.get_td_parent_element(it, rec)  
        else:
            res = rec
        
        if vertical_align and txt != "":
            div_vertical = HtmlElement("div", vertical_align)
            div_vertical.add_element(HtmlElement("text", None, txt))
            rec.add_element(div_vertical)

        return res

    def is_in_cell(self, it): 
        if it.parent and it.parent.type == "RowCell":
            return True
        return False

    def get_td_parent_element(self, it, element):
        if not self.is_in_cell(it):
            return element
        td = HtmlElement("td", None)
        if it.parent.col_span > 1:
            td.add_attribute("colspan", it.parent.col_span)
        td.add_element(element) 
        return td

    def add_style(self, html_element, it, text=None, ignore_list=[]):
        if not html_element.id:
            return
        
        i = self.style_helper.add_style(html_element.tag, 
                        html_element.id, 
                        self.get_style(it, ignore_list))
        
        html_element.id = "{0}-{1}".format(html_element.id, i)

    def get_style(self, it, ignore_list=[]):
        properties=[] 
        self.add_style_property('overflow', 'hidden', ignore_list,  properties)
        self.add_style_property('height', "{0}mm".format(it.height), ignore_list,  properties)
        self.add_style_property('width', "{0}mm".format(it.width), ignore_list,  properties)
        if it.style.background_color:
            self.add_style_property('background-color', it.style.background_color.hex, ignore_list,  properties) 
        self.add_style_property('border-collapse', 'collapse', ignore_list,  properties)
        self.add_style_property('border-style', "{0} {1} {2} {3}".format(
                self.get_border_style_width(it.style.border.style.top), 
                self.get_border_style_width(it.style.border.style.right),
                self.get_border_style_width(it.style.border.style.bottom),
                self.get_border_style_width(it.style.border.style.left)), ignore_list,  properties)
        self.add_style_property('border-width', "{0}mm {1}mm {2}mm {3}mm".format(
                self.get_border_style_width(it.style.border.width.top), 
                self.get_border_style_width(it.style.border.width.right),
                self.get_border_style_width(it.style.border.width.bottom),
                self.get_border_style_width(it.style.border.width.left)), ignore_list,  properties)
        self.add_style_property('border-color', "{0} {1} {2} {3}".format(
                it.style.border.color.top.hex, 
                it.style.border.color.right.hex,
                it.style.border.color.bottom.hex,
                it.style.border.color.left.hex), ignore_list,  properties)

        if it.type == "PageText":
            self.add_style_property('color', it.style.text.color.hex, ignore_list,  properties)
            self.add_style_property('vertical-align', it.style.text.vertical_align, ignore_list,  properties)
            self.add_style_property('font-family', it.style.text.font_family, ignore_list,  properties)
            self.add_style_property('font-weight', it.style.text.font_weight, ignore_list,  properties)
            self.add_style_property('font-style', it.style.text.font_style, ignore_list,  properties)
            self.add_style_property('font-size', "{0}mm".format(it.style.text.font_size.value), ignore_list,  properties)
            self.add_style_property('text-align', it.style.text.text_align, ignore_list,  properties)
            self.add_style_property('text-decoration', it.style.text.text_decoration, ignore_list,  properties)
            self.add_style_property('padding', "{0}mm {1}mm {2}mm {3}mm".format(
                                it.style.text.padding_top.value,
                                it.style.text.padding_right.value,
                                it.style.text.padding_left.value,
                                it.style.text.padding_bottom.value), ignore_list,  properties)

        res = ""
        for p in properties:
            res = "{0} {1}".format(res, p)

        return res

    def add_style_property(self, prop, value, ignore_list, property_list):
        if prop not in ignore_list:
            property_list.append("{0}:{1};".format(prop, value))

    def get_border_style_width(self, bs):
        return "none" if not bs.value else bs.value

    def write_to_file(self):
        lines = []
        lines = self.doc.get_element()
        try:
            f = open(self.result_file, "w")
            try:
                for l in lines:
                    f.write(l.encode('utf-8', 'replace'))
            finally:
                f.close()
        except IOError as e:
            raise_error_with_log("I/O Error trying to write to file '{0}'. {1}.".format(self.result_file, e.strerror))
        except:
            raise_error_with_log("Unexpected error trying to write to file '{0}'. {1}.".format(self.result_file, sys.exc_info()[0]))

    def help(self):
        "HtmlRender help"


class StyleHelper(object):
    def __init__(self):
        self.style_object_list={}
        self.style_list={}
        
    def add_style(self, tag, id, style):
        if self.style_object_list.has_key(id):
            obj = self.style_object_list[id]
        else:
            obj = StyleHelperObject(tag, id)
        i = obj.get_id_enum(style)
        self.style_object_list[id] = obj
        
        key = "{0}#{1}-{2}".format(tag, id, i)
        if not self.style_list.has_key(key):
            self.style_list[key] = style
        
        return i

        
class StyleHelperObject(object):
    def __init__(self, tag, id):
        self.style_list={}
    
    def get_id_enum(self, style):
        if self.style_list.has_key(style):
            return self.style_list[style]
        i = len(self.style_list) + 1
        self.style_list[style] = i
        return i


class HtmlElement(object):
    def __init__(self, tag, element_id, text=None):
        if element_id:
            element_id = element_id.replace(".","_")
        self.id = element_id
        self.tag = tag
        self.text=text 
        self.attributes = None
        self.content = []

    def add_attribute(self, key, value):
        if not self.attributes:
            self.attributes = "{0}='{1}'".format(key, value)
        else: 
            self.attributes = "{0} {1}='{2}'".format(self.attributes, key, value)

    def add_element(self, el):
        self.content.append(el)

    def get_element(self):
        result = []
        if self.id:
            self.add_attribute("id", self.id)
        if self.text and len(self.content) == 0:
            return [self.text,]
        if self.tag == "DOCTYPE":
            result.append("<!DOCTYPE html>\n")
        else:
            c = "<{0}".format(self.tag)
            if self.attributes:
                c = "{0} {1}>".format(c, self.attributes)
            else:
                c = c + ">\n"
            result.append(c)

        el_result = []
        for el in self.content:
            el_result.extend(el.get_element())
        result.extend(el_result)

        if self.tag != "DOCTYPE":
            result.append("</{0}>\n".format(self.tag))
         
        return result

