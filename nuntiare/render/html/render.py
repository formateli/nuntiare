# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import sys
import html
from .. render import Render
from ... import LOGGER
from ... outcome.page_item import PageItemsInfo


class HeaderFooterRectangle(object):
    def __init__(self, report, definition):
        self.type = 'PageRectangle'
        self.name = None
        self.width = None
        self.parent = None
        self.top = 0
        self.left = 0
        self.height = report.get_value(
            definition, 'Height', 0)
        self.items_info = PageItemsInfo(
            report, definition, self)
        self.style = report.get_style(
            definition, self.type)

    def get_item_list(self):
        if self.items_info:
            return self.items_info.item_list


class HtmlRender(Render):
    def __init__(self):
        super(HtmlRender, self).__init__(extension='html')
        self.doc = None
        self.style_helper = _StyleHelper()

    def render(self, report, overwrite):
        super(HtmlRender, self).render(report, overwrite)

        report.globals.TotalPages = 1
        report.globals.PageNumber = 1

        self.doc = _HtmlElement('DOCTYPE', None)
        html = _HtmlElement('html', None)
        head = self._get_head(report)
        html.add_element(head)
        self.doc.add_element(html)

        body = _HtmlElement('body', None)

        container = _HtmlElement('div', 'container')
        container.add_attribute(
            'style', 'width:{0}pt'.format(report.result.available_width))

        self._get_report_header_footer(
            'header', report, report.result.header, container)
        self._get_report_body(report, container)
        self._get_report_header_footer(
            'footer', report, report.result.footer, container)

        body.add_element(container)
        html.add_element(body)

        str_style = "@page {size: " + str(report.result.width) + \
            "pt " + str(report.result.height) + "pt; " + \
            "margin-top: " + str(report.result.margin_top) + "pt; " \
            "margin-right: " + str(report.result.margin_right) + "pt; " \
            "margin-bottom: " + str(report.result.margin_bottom) + "pt; " \
            "margin-left: " + str(report.result.margin_left) + "pt;}\n"
        str_style += ".page-break	{page-break-before: always;}\n"
        str_style += ".div_Middle "  \
            "{display: inline-block; position: relative; top: 50%; " \
            "transform: translateY(-50%); vertical-align: middle;}\n"
        str_style += ".div_Bottom " \
            "{display: inline-block; position: relative; top: 100%; " \
            "transform: translateY(-100%); vertical-align: middle;}\n"

        for key, value in self.style_helper.style_list.items():
            str_style += key + "{" + value + "}\n"

        style = _HtmlElement('style', None)
        style.add_attribute('type', 'text/css')
        style.add_element(_HtmlElement('text', None, str_style))
        head.add_element(style)

        self._write_to_file()

    def _get_head(self, report):
        head = _HtmlElement("head", None)
        title = _HtmlElement("title", None)
        title.add_element(_HtmlElement(
            "text", None, report.globals.ReportName))
        head.add_element(title)
        return head

    def _get_report_header_footer(
            self, name, report, header_footer, container):
        if not header_footer or not header_footer.definition:
            return
        rec = HeaderFooterRectangle(report, header_footer.definition)
        rec.name = "div_" + name
        rec.width = report.result.available_width
        items = [rec, ]
        report_header = _HtmlElement("div", "{0}_container".format(name))
        if name == "header":
            report_header.add_attribute(
                "style", "height:{0}pt".format(header_footer.height))
        else:
            report_header.add_attribute(
                "style", "clear:both; height:{0}pt".format(
                    header_footer.height))
        container.add_element(report_header)
        self._render_items(items, report_header)

    def _get_report_body(self, report, container):
        report_body = _HtmlElement("div", "body_container")
        report_body.add_attribute(
            "style",
            "float:left; padding:1pt 1pt 1pt 1pt; width:{0}pt".format(
                report.result.available_width))
        container.add_element(report_body)
        self._render_items(report.result.body.items.item_list,
                           report_body)

    def _render_items(self, items, container):
        if not items:
            return
        for it in items:
            if it.type == 'PageLine':
                continue  # Not supported
            if it.type in ['PageRectangle', 'PageText']:
                el = self._get_rectangle(it)
            if it.type == 'PageTablix':
                el = self._get_grid(it)

            break_ = None
            break_el = None
            if hasattr(it, 'page_break'):
                break_ = it.page_break
                if break_:
                    if break_ in ['Start', 'StartAndEnd']:
                        break_el = _HtmlElement('div', None)
                        break_el.add_attribute('class', 'page-break')
                        container.add_element(break_el)

            container.add_element(el)

            if break_ and break_ in ['End', 'StartAndEnd']:
                break_el = _HtmlElement('div', None)
                break_el.add_attribute('class', 'page-break')
                container.add_element(break_el)

    def _set_tablix_column_header(self, tablix, it):
        def get_column_header_rows(hierarchy):
            rows = []
            for size in hierarchy.cumulative_sizes:
                rows.append(_HtmlElement('tr', None))
            return rows

        def add_sub_items(items, header_rows):
            for sub in items:
                if sub.level is None:
                    continue
                row = header_rows[sub.level]
                self._render_items(sub.cell.object.item_list, row)
                if sub.sub_items:
                    add_sub_items(sub.sub_items, header_rows)

        header_rows = get_column_header_rows(it.column_hierarchy)

        if it.tablix_corner:
            # Draw corner
            i = 0
            for rw in header_rows:
                row = it.tablix_corner.rows[i]
                for cell in row.cells:
                    if not cell.object:
                        continue
                    self._render_items(cell.object.item_list, rw)
                i += 1
        elif it.row_hierarchy.has_header():
            # Leave blank space for corner
            td_corner = _HtmlElement('td', None)
            td_corner.add_attribute('colspan', len(
                it.row_hierarchy.cumulative_sizes))
            td_corner.add_attribute('rowspan', len(
                it.column_hierarchy.cumulative_sizes))
            header_rows[0].add_element(td_corner)

        for grp in it.column_header_groups:
            rw = header_rows[grp.level]
            self._render_items(grp.cell.object.item_list, rw)
            if grp.sub_items:
                add_sub_items(grp.sub_items, header_rows)

        for r in header_rows:
            tablix.add_element(r)

    def _get_grid(self, it):
        def render_header(items, rows, count):
            for sub in items:
                if not sub.cell.object:
                    count = render_header(
                        sub.sub_items, rows, count)
                rw = rows[count]
                if sub.cell.object:
                    self._render_items(
                        sub.cell.object.item_list, rw)
                count = render_header(
                    sub.sub_items, rows, count)
            return count + 1

        tablix = _HtmlElement('table', it.name)
        self._add_style(tablix, it, ignore_list=['height', ])

        if it.column_hierarchy.has_header():
            self._set_tablix_column_header(tablix, it)

        if it.row_hierarchy.has_header():
            row_count = 0
            for header_item in it.row_header_groups:
                rows = []
                x = 0
                while x < header_item.last_items_count:
                    rows.append(_HtmlElement('tr', None))
                    x += 1

                if not header_item.cell.object:
                    render_header(
                        header_item.sub_items, rows, 0)
                else:
                    rw = rows[0]
                    self._render_items(
                        header_item.cell.object.item_list, rw)
                    render_header(
                        header_item.sub_items, rows, 0)

                for rw in rows:
                    row = it.grid_body.rows[row_count]
                    for cell in row.cells:
                        if not cell.object:
                            continue
                        self._render_items(cell.object.item_list, rw)
                    tablix.add_element(rw)
                    row_count += 1
        else:
            for row in it.grid_body.rows:
                rw = _HtmlElement('tr', None)
                for cell in row.cells:
                    if not cell.object:
                        continue
                    self._render_items(cell.object.item_list, rw)
                tablix.add_element(rw)

        res = self._get_td_parent_element(it, tablix)
        return res

    def _get_rectangle(self, it):
        in_cell = self._is_in_cell(it)
        is_textbox = True if it.type == 'PageText' else False
        vertical_align = None

        txt = ''
        if is_textbox:
            txt = it.value_formatted
            if txt:
                txt = html.escape(txt)
                txt = txt.replace('\n', '<br>')  # New line
            else:
                txt = ''

        if not it.parent or it.parent.type == 'PageRectangle':
            # It is just a rectangle or a Textbox belonging to a rectangle.
            is_div = True
        else:  # It is a Textbox belonging to a cell.
            is_div = False

        ignore = []
        rec = None
        sub_rec = None
        if is_div:
            rec = _HtmlElement('div', it.name)
            if it.name == 'div_header' or it.name == 'div_footer':
                ignore.append('overflow')
            if is_textbox and (it.can_grow or it.can_shrink):
                ignore.append('height')
            if it.style.vertical_align in ('Middle', 'Bottom'):
                vertical_align = it.style.vertical_align
            self._add_style(rec, it, ignore_list=ignore)
        else:
            rec = _HtmlElement('td', it.name)
            it.height = it.parent.height
            it.width = it.parent.width
            if it.parent.col_span > 1:
                rec.add_attribute('colspan', it.parent.col_span)
            if it.parent.row_span > 1:
                rec.add_attribute('rowspan', it.parent.row_span)
            if is_textbox and not it.can_grow:
                sub_rec = _HtmlElement('div', 'div_' + it.name)
                rec.add_element(sub_rec)
            if sub_rec:
                ignore = [
                    'border-collapse',
                    'border-style', 'border-width', 'border-color',
                    'color', 'vertical-align', 'font-family',
                    'font-weight', 'font-style', 'font-size',
                    'text-align', 'text-decoration', 'padding'
                ]

                self._add_style(
                    sub_rec, it, ignore_list=ignore)
                self._add_style(rec, it, ['height', ])
                if it.style.vertical_align in ('Middle', 'Bottom'):
                    vertical_align = it.style.vertical_align
            else:
                self._add_style(rec, it, [])

        if txt != '' and not vertical_align:
            if sub_rec:
                sub_rec.add_element(_HtmlElement('text', None, txt))
            else:
                rec.add_element(_HtmlElement('text', None, txt))

        self._render_items(it.get_item_list(), rec)

        if is_div and in_cell:
            res = self._get_td_parent_element(it, rec)
        else:
            res = rec

        if vertical_align and txt != '':
            div_vertical = _HtmlElement('div', vertical_align)
            div_vertical.add_element(_HtmlElement('text', None, txt))
            if is_div:
                rec.add_element(div_vertical)
            else:
                if sub_rec:
                    sub_rec.add_element(div_vertical)

        return res

    def _is_in_cell(self, it):
        if it.parent and it.parent.type == 'RowCell':
            return True

    def _get_td_parent_element(self, it, element):
        if not self._is_in_cell(it):
            return element
        td = _HtmlElement('td', None)
        if it.parent.col_span > 1:
            td.add_attribute('colspan', it.parent.col_span)
        td.add_element(element)
        return td

    def _add_style(self, html_element, it, ignore_list=[]):
        if not html_element.id:
            return

        i = self.style_helper.add_style(
            html_element.tag,
            html_element.id,
            self._get_style(it, ignore_list))

        html_element.id = "{0}-{1}".format(html_element.id, i)

    def _get_style(self, it, ignore_list=[]):
        properties = []
        self._add_style_property(
            'overflow', 'hidden', ignore_list,  properties)
        self._add_style_property(
            'height', "{0}pt".format(it.height), ignore_list,  properties)
        self._add_style_property(
            'width', "{0}pt".format(it.width), ignore_list,  properties)
        if it.style.background_color:
            self._add_style_property(
                'background-color',
                it.style.background_color,
                ignore_list, properties)
        self._add_style_property(
            'border-collapse', 'collapse',
            ignore_list, properties)
        self._add_style_property(
            'border-style', "{0} {1} {2} {3}".format(
                self._get_border_style_width(
                    it.style.top_border.border_style),
                self._get_border_style_width(
                    it.style.right_border.border_style),
                self._get_border_style_width(
                    it.style.bottom_border.border_style),
                self._get_border_style_width(
                    it.style.left_border.border_style)),
            ignore_list, properties)
        self._add_style_property(
            'border-width', "{0}pt {1}pt {2}pt {3}pt".format(
                self._get_border_style_width(
                    it.style.top_border.width),
                self._get_border_style_width(
                    it.style.right_border.width),
                self._get_border_style_width(
                    it.style.bottom_border.width),
                self._get_border_style_width(
                    it.style.left_border.width)),
            ignore_list, properties)
        self._add_style_property(
            'border-color', "{0} {1} {2} {3}".format(
                it.style.top_border.color,
                it.style.right_border.color,
                it.style.bottom_border.color,
                it.style.left_border.color),
            ignore_list,  properties)

        if it.type == "PageText":
            self._add_style_property(
                'color', it.style.color,
                ignore_list,  properties)
            self._add_style_property(
                'vertical-align', it.style.vertical_align,
                ignore_list, properties)
            self._add_style_property(
                'font-family', it.style.font_family,
                ignore_list,  properties)
            self._add_style_property(
                'font-weight', it.style.font_weight,
                ignore_list,  properties)
            self._add_style_property(
                'font-style', it.style.font_style,
                ignore_list,  properties)
            self._add_style_property(
                'font-size', "{0}pt".format(it.style.font_size),
                ignore_list,  properties)
            self._add_style_property(
                'text-align', it.style.text_align,
                ignore_list, properties)
            self._add_style_property(
                'text-decoration', it.style.text_decoration,
                ignore_list, properties)
            self._add_style_property(
                'padding', "{0}pt {1}pt {2}pt {3}pt".format(
                    it.style.padding_top,
                    it.style.padding_right,
                    it.style.padding_bottom,
                    it.style.padding_left),
                ignore_list,  properties)

        res = ''
        for p in properties:
            res += ' ' + p
        return res

    def _add_style_property(self, prop, value, ignore_list, property_list):
        if prop not in ignore_list:
            property_list.append("{0}:{1};".format(prop, value))

    def _get_border_style_width(self, bs):
        return 'none' if not bs else bs

    def _write_to_file(self):
        lines = []
        lines = self.doc.get_element()
        try:
            f = open(self.result_file, "wb")
            try:
                for l in lines:
                    if sys.version_info[0] == 2:  # python2
                        f.write(l)
                    else:
                        f.write(l.encode('utf-8'))
            finally:
                f.close()
        except IOError as e:
            LOGGER.error(
                "I/O Error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e.strerror),
                True, "IOError")
        except Exception:
            LOGGER.error(
                "Unexpected error trying to write to file '{0}'. {1}.".format(
                    self.result_file, sys.exc_info()[0]),
                True, "IOError")

    def help(self):
        'HtmlRender help'


class _StyleHelper(object):
    def __init__(self):
        self.style_object_list = {}
        self.style_list = {}

    def add_style(self, tag, id, style):
        if id in self.style_object_list:
            obj = self.style_object_list[id]
        else:
            obj = _StyleHelperObject(tag, id)
        i = obj.get_id_enum(style)
        self.style_object_list[id] = obj

        key = ".{0}_{1}-{2}".format(tag, id, i)
        if key not in self.style_list:
            self.style_list[key] = style

        return i


class _StyleHelperObject(object):
    def __init__(self, tag, id):
        self.style_list = {}

    def get_id_enum(self, style):
        if style in self.style_list:
            return self.style_list[style]
        i = len(self.style_list) + 1
        self.style_list[style] = i
        return i


class _HtmlElement(object):
    def __init__(self, tag, element_id, text=None):
        if element_id:
            element_id = element_id.replace('.', '_')
        self.id = element_id
        self.tag = tag
        self.text = text
        self.attributes = None
        self.content = []

    def add_attribute(self, key, value):
        if not self.attributes:
            self.attributes = "{0}='{1}'".format(
                key, value)
        else:
            self.attributes = "{0} {1}='{2}'".format(
                self.attributes, key, value)

    def add_element(self, el):
        self.content.append(el)

    def get_element(self):
        result = []
        if self.id:
            self.add_attribute("class", self.tag + "_" + self.id)
        if self.text and len(self.content) == 0:
            return [self.text, ]
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
