# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
from tkinter import ttk
import nuntiare.definition.element as nuntiare


class NuntiareXmlNode(ttk.Treeview):

    # Cache elements meta.
    # key: Element name
    # Value: Dictionary of Meta
    _element_meta = {}

    def __init__(self, master,
                 designer,
                 xscrollcommand,
                 yscrollcommand):
        super(NuntiareXmlNode, self).__init__(
                master,
                columns=('name'),
                displaycolumns=(),
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

        self._doc = None  # dom document
        self._designer = designer
        self._get_element_meta()

        # Allow horizontal scrolling
        # TODO width should be adjusted according to
        # number of decendents nodes.
        self.column("#0", width=600, stretch=False)

        self._property = None
        self._last_item = None

        # item: [xml_node, report_item]
        self._values = {}

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

        # TODO Verify that comment does not already exists, avoiding duplicate
        comment = dom.createComment(
            ' Created by Pluma - The Nuntiare Designer tool.\n'
            '     Copyright Fredy Ramirez - https://formateli.com ')
        dom.insertBefore(comment, root)

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
            report_item = self._designer.sections.info
        elif node.nodeName in ('PageHeader', 'PageFooter', 'Body'):
            report_item = \
                self._designer.sections._sections[node.nodeName].info
        elif node.nodeName == 'Style':
            ri_item = self.parent(item)
            ri_ri = self._values[ri_item][1]
            ri_ri.Style.set_tree_item(item)
        self._values[item][1] = report_item
        self.tag_bind('element', '<<TreeviewSelect>>', self._item_clicked)
        self._show_item_name(item)

        if node.nodeName == 'PageHeader':
            self._designer.sections.set_page_item(item)
        if node.nodeName in ('PageHeader', 'PageFooter', 'Body'):
            self._designer.sections.get_section(node.nodeName).set_item(item)
        return item

    def _show_item_name(self, item):
        text = self._get_node_value(item, 'Name')
        if text is not None:
            text = self.item(item, 'text') + ' (' + text + ')'
            self.item(item, text=text)

    def _set_node_value(self, item, name, value):
        print('set_node_value ' + name + ' ' + str(value))
        node = self._get_xml_sub_node(item, name)
        if node is None:
            print(value)
            master = self._values[item][0]
            el = self._doc.createElement(name)
            text = self._doc.createTextNode(value)
            el.appendChild(text)
            master.appendChild(el)
        else:
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
                n.nodeValue = value
                return
        text = self._doc.createTextNode(value)
        node.parent.appendChild(text)

    def _get_node_text(self, node):
        for n in node.childNodes:
            if n.nodeName in ('#text'):
                return n.nodeValue

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
            property_ = self._property.add_property(
                            key, meta.constant)
            # Get the value, if any, in current node
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
        self._set_node_value(item, property_._text, property_.get_value())

        name = self.set(item, 'name')
        if name == 'Page' and property_._text not in (
                'Columns', 'ColumnSpacing'):
            self._designer.sections.update()
        elif name in ('PageHeader', 'PageFooter') and \
                    property_._text in ('Height'):
            self._designer.sections.get_section[name].update()
        elif name in nuntiare._REPORT_ITEMS and \
                property_._text in ('Top', 'Left', 'Height', 'Width'):
            report_item = self._values[item][1]
            report_item.update(property_._text)
        elif name == 'Style':
            parent = self.parent(item)
            report_item = self._values[parent][1]
            report_item.Style.update(property_._text)


class PropertyFrame(ttk.Frame):
    def __init__(self, master):
        super(PropertyFrame, self).__init__(master)
        self._bind_callbacks = {}

    def register_property_event(self, name):
        self._bind_callbacks = {name: []}

    def bind(self, event, callback):
        if event in self._bind_callbacks:
            self._bind_callbacks[event].append(callback)
        else:
            super(PropertyFrame, self).bind(event, callback)

    def fire_event(self, event, data):
        callbacks = self._bind_callbacks[event]
        for cb in callbacks:
            cb(data)


class NuntiareProperty(PropertyFrame):
    def __init__(self, master):
        super(NuntiareProperty, self).__init__(master)
        self._properties = {}
        self._row_count = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self._item = None

        self.register_property_event('property_changed')

    def add_property(self, text, required):
        id_ = text + '_' + str(required)
        if id_ not in self._properties:
            self._properties[id_] = [
                    ttk.Label(self, text=text),
                    PropertyItem(self, text, required),
                ]
            self._properties[id_][1].bind(
                'property_focusout', self._property_focusout)

        property_ = self._properties[id_]
        property_[0].grid(row=self._row_count, column=0, sticky='wens')
        property_[1].grid(row=self._row_count, column=1, sticky='wens')
        self._row_count += 1
        return property_[1]

    def set_item(self, item):
        if item != self._item:
            self._item = item
            self.clear()

    def get_item(self):
        return self._item

    def clear(self):
        wgs = self.grid_slaves()
        for wg in wgs:
            wg.grid_forget()
        self._row_count = 0

    def _property_focusout(self, property_):
        self.fire_event('property_changed', [self, property_])


class PropertyItem(PropertyFrame):
    def __init__(self, master, text, required):
        super(PropertyItem, self).__init__(master)

        self._entry = ttk.Entry(self)
        self._entry.grid(row=0, column=0, sticky='wens')

        self._text = text
        self._required = required
        self._value = None
        self._default = None

        self.register_property_event('property_focusout')
        self.bind('<FocusOut>', self._focusout)

    def set_value(self, value, default):
        self._value = value
        self._default = default
        self._entry.delete(0, 'end')
        if value is not None:
            self._entry.insert(0, self._value)
        elif self._default is not None:
            self._entry.insert(
                0, '[Default: ' + str(self._default) + ']')

    def get_value(self):
        if self._value:
            return self._value
        if not self._value and self._required and self._default:
            return self._default

    def _focusout(self, event):
        value = self._entry.get()
        if value != self._value and not value.startswith('[Default: '):
            self._value = value
            self.fire_event('property_focusout', self)
