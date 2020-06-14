# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
import tkinter as tk
from tkinter import ttk
import nuntiare.definition.element as nuntiare
from ...menu_manager import MenuManager


class NuntiareXmlNode(ttk.Treeview):

    # Cache elements meta.
    # key: Element name
    # Value: Dictionary of Meta
    _element_meta = {}

    # Report item menu images
    _ri_images = {
        'Line': 'line-24px',
        'Rectangle': 'rectangle-24px',
        'Textbox': 'textbox-24px',
        'Image': 'image-24px',
        'Subreport': 'file_paste-24px',
        'CustomReportItem': 'image-24px',
        'Tablix': 'grid-24px',
        'Chart': 'chart-24px'
        }

    def __init__(self, master,
                 designer,
                 xscrollcommand,
                 yscrollcommand):
        super(NuntiareXmlNode, self).__init__(
                master,
                columns=('name'),
                displaycolumns=(),
                selectmode='browse',
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

        self._doc = None  # dom document
        self._designer = designer
        self._menu_prefix = designer.menu_prefix
        self._get_element_meta()

        # Allow horizontal scrolling
        # TODO width should be adjusted according to
        # number of decendents nodes.
        self.column("#0", width=600, stretch=False)

        self._property = None
        self._last_item = None

        # item: [xml_node, report_item]
        self._values = {}
        # element_name: menu
        self._menu_add = {}

        self._item_menu = MenuManager.new_menu(
                self._menu_prefix + 'treview', None,
                master=self, image_size='24x24')
        MenuManager.add_command(
                self._menu_prefix + 'treview', 'up', 'Up',
                None, self._item_up, image='arrow_upward-24px',
                state=tk.NORMAL)
        MenuManager.add_command(
                self._menu_prefix + 'treview', 'down', 'Down',
                None, self._item_up, image='arrow_downward-24px',
                state=tk.NORMAL)
        MenuManager.add_command(
                self._menu_prefix + 'treview', 'remove', 'Remove',
                None, self._item_up, image='clear-24px',
                state=tk.NORMAL)
        MenuManager.add_separator(self._menu_prefix + 'treview')
        MenuManager.add_command(
                self._menu_prefix + 'treview', 'copy', 'Copy',
                None, self._item_up, image='file_copy-24px',
                state=tk.NORMAL)
        MenuManager.add_command(
                self._menu_prefix + 'treview', 'paste', 'Paste',
                None, self._item_up, image='file_paste-24px',
                state=tk.NORMAL)
        MenuManager.add_separator(self._menu_prefix + 'treview')
        MenuManager.new_menu(
                self._menu_prefix + 'treview' + '_add',
                self._menu_prefix + 'treview',
                image_size='24x24')
        MenuManager.add_command(
                self._menu_prefix + 'treview' + '_add',
                'dummy', 'dummy', None, None,
                state=tk.NORMAL)

    def _item_up(self):
        pass

    @classmethod
    def _get_element_meta(cls):
        def add_meta(el):
            class_ = getattr(nuntiare, el)
            meta = nuntiare.Element._get_element_list(class_)
            NuntiareXmlNode._element_meta[el] = meta

        if NuntiareXmlNode._element_meta:
            return
        for el in nuntiare._ELEMENT_CLASSES:
            add_meta(el)
        for el in nuntiare._EXPRESSION_LIST_CLASSES:
            add_meta(el)

    def get_xml_text(self):
        # This routine is necesary to avoid
        # lines spaces when using toprettyxml()
        data = self._doc.toprettyxml(indent='  ', encoding='utf-8')
        data = data.decode('utf-8')

        reparsed = minidom.parseString(data)
        data = ''
        for line in reparsed.toprettyxml(indent=' ').split('\n'):
            st = line.strip()
            if st:
                data += st

        dom = minidom.parseString(data)
        root = dom.getElementsByTagName('Nuntiare')[0]

        # Verify comments.
        comment_nuntiare = (' This file is part of Nuntiare project.\n'
            '     The COPYRIGHT file at the top level of this repository\n'
            '     contains the full copyright notices and license terms. ')
        comment_pluma = (' Created by Pluma - The Nuntiare Designer tool.\n'
            '     Copyright Fredy Ramirez - https://formateli.com ')
        for node in dom.childNodes:
            if node.nodeName in ('#comment'):
                val = node.nodeValue
                if val.startswith(
                        ' This file is part of Nuntiare project.'):
                    comment = dom.createComment(comment_nuntiare)
                    dom.replaceChild(comment, node)
                elif val.startswith(
                        ' Created by Pluma - The Nuntiare Designer tool.'):
                    dom.removeChild(node)
        dom.insertBefore(dom.createComment(comment_pluma), root)

        return dom.toprettyxml(indent='  ', encoding='utf-8')

    def set_property(self, property_):
        self._property = property_
        self._property.bind('property_changed', self._property_changed)
        self._property.clear()

    def parse(self, xml, is_file):
        if is_file:
            self._doc = minidom.parse(xml)
        else:
            self._doc = minidom.parseString(xml)
        root = self._doc.getElementsByTagName('Nuntiare')[0]
        item = self._add_node_element('', root)
        self._get_nodes(root, item)

    def _get_nodes(self, node, parent):
        for n in node.childNodes:
            if n.nodeName in ('#comment', '#text'):
                continue
            if (n.nodeName in nuntiare._ELEMENT_CLASSES
                    or n.nodeName in nuntiare._EXPRESSION_LIST_CLASSES):
                item = self._add_node_element(parent, n)
                self._get_nodes(n, item)

    def _add_node_element(self, parent, node):
        item = self.insert(
                parent, 'end',
                text=node.nodeName,
                values=(node.nodeName),
                tags=('element'))
        self._values[item] = [node, None]
        report_item = None
        if node.nodeName in nuntiare._REPORT_ITEMS:
            report_item = self._designer.sections.add_report_item(
                    node.nodeName, item)
        elif node.nodeName == 'Page':
            report_item = self._designer.sections.page_info
            self._designer.sections.set_page_item(item)
        elif node.nodeName in ('PageHeader', 'PageFooter', 'Body'):
            report_item = \
                self._designer.sections._sections[node.nodeName].info
            self._designer.sections.get_section(node.nodeName).set_item(item)
        elif node.nodeName in ('Style', 'Border', 'RightBorder',
                'LeftBorder', 'TopBorder', 'BottomBorder'):
            ri_item = self.parent(item)
            ri_ri = self._values[ri_item][1]
            obj = getattr(ri_ri, node.nodeName)
            obj.set_tree_item(item)
            if node.nodeName == 'Style':
                report_item = ri_ri.Style

        self._values[item][1] = report_item
        self.tag_bind('element', '<<TreeviewSelect>>', self._item_clicked)
        self.tag_bind('element', '<3>', self._item_3_clicked)
        self._show_item_name(item)
        return item

    def _create_sub_element(self, item, element):
        node = self._values[item][0]
        el = self._doc.createElement(element)
        node.appendChild(el)
        return self._add_node_element(item, el)

    def _show_item_name(self, item):
        text = self._get_node_value(item, 'Name')
        if text is not None:
            text = self.item(item, 'text') + ' (' + text + ')'
            self.item(item, text=text)

    def _set_node_value(self, item, name, value):
        node = self._get_xml_sub_node(item, name)
        if node is None:
            master = self._values[item][0]
            node = self._doc.createElement(name)
            master.appendChild(node)
            if value is None:
                return
        self._set_node_text(node, value)

    def _get_node_value(self, item, name):
        node = self._values[item][0]
        for n in node.childNodes:
            if n.nodeName == name:
                return self._get_node_text(n)

    def _get_xml_sub_node(self, item, name):
        node = self._values[item][0]
        for n in node.childNodes:
            if n.nodeName == name:
                return n

    def _set_node_text(self, node, value):
        for n in node.childNodes:
            if n.nodeName in ('#text'):
                if value is None:
                    node.removeChild(n)
                    return
                else:
                    n.nodeValue = value
                    return
        text = self._doc.createTextNode(value)
        node.appendChild(text)

    def _get_node_text(self, node):
        for n in node.childNodes:
            if n.nodeName in ('#text'):
                return n.nodeValue

    def _item_3_clicked(self, event):
        item = self.identify_row(event.y)

        self.focus_set()
        self.focus(item)
        self.selection_set(item)
        self._item_clicked(event)

        self._item_menu.delete(7)
        self._get_add_menu(item)
        self._item_menu.post(event.x_root, event.y_root)

    def _add_element(self, values):
        item = values[0]
        element = values[1]
        meta = values[2]

        if meta.card in (nuntiare.Card.ONE, nuntiare.Card.ZERO_ONE):
            for it in self.get_children(item):
                if element == self.set(it, 'name'):
                    # Ignore. Just one element of
                    # this type
                    return

        new_item = self._create_sub_element(item, element)
        self.focus(new_item)
        self.see(new_item)
        self.selection_set(new_item)
        self._item_clicked(None)

    def _get_add_menu(self, item):
        name = self.set(item, 'name')
        parent = self._menu_prefix + 'treview'
        menu = parent + '_add_' + name

        if name in self._menu_add:
            MenuManager.add_cascade('Add', parent, menu)
            return

        if len(NuntiareXmlNode._element_meta[name]) == 0:
            return

        MenuManager.new_menu(menu, parent, image_size='24x24')

        for key, meta in NuntiareXmlNode._element_meta[name].items():
            if (meta.type == nuntiare.Element.ELEMENT or
                    meta.type == nuntiare.Element.EXPRESSION_LIST):
                image = None
                if key in nuntiare._REPORT_ITEMS:
                    image = NuntiareXmlNode._ri_images[key]
                MenuManager.add_command(
                    menu, key, key, None,
                    command=lambda x=[item, key, meta]: self._add_element(x),
                    image=image, state=tk.NORMAL)

        MenuManager.add_cascade('Add', parent, menu)
        self._menu_add[name] = menu

    def _item_clicked(self, event):
        sel = self.selection()
        item = sel[0] if sel else None
        if self._last_item == item:
            return
        self._last_item = item
        if item is None:
            return

        name = self.set(item, 'name')
        self._property.set_item(item)

        for key, meta in NuntiareXmlNode._element_meta[name].items():
            if (not meta or meta.type == nuntiare.Element.ELEMENT
                    or meta.type == nuntiare.Element.EXPRESSION_LIST):
                continue
            property_ = self._property.add_property(key, meta.type)
            property_.set_value(
                    self._get_node_value(item, key), meta.default)

    def get_report_item_info(self, item):
        itm = item
        section = None
        report_item_parent = None
        name = self.set(item, 'name')
        meta = NuntiareXmlNode._element_meta[name]
        while True:
            parent = self.parent(itm)
            if not parent:
                break
            if self._values[parent][0].nodeName in (
                    'PageHeader', 'PageFooter', 'Body'):
                section = self._values[parent][0].nodeName
            if self._values[parent][1] is not None:
                report_item_parent = parent
            if section is not None and report_item_parent is not None:
                break
            itm = parent
        return section, report_item_parent, meta

    def _property_changed(self, event):
        master = event[0]
        property_ = event[1]
        item = master.get_item()
        self._set_node_value(item, property_.name, property_.get_value())

        name = self.set(item, 'name')
        if name == 'Page' and property_.name not in (
                'Columns', 'ColumnSpacing'):
            self._designer.sections.update()
        elif name in ('PageHeader', 'PageFooter') and \
                    property_.name in ('Height'):
            self._designer.sections.get_section[name].update()
        elif name in nuntiare._REPORT_ITEMS and \
                property_.name in ('Top', 'Left', 'Height', 'Width'):
            report_item = self._values[item][1]
            report_item.update(property_.name)
        elif name in ('Style', 'Border', 'RightBorder',
                'LeftBorder', 'TopBorder', 'BottomBorder'):
            parent = self.parent(item)
            report_item = self._values[parent][1]
            obj = getattr(report_item, name)
            obj.update(property_.name)
