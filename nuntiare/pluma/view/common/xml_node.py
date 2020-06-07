# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
from tkinter import ttk
import nuntiare.definition.element as nuntiare


class NuntiareXmlNode(ttk.Treeview):

    _properties = {}

    def __init__(self, master,
                 xscrollcommand,
                 yscrollcommand):
        super(NuntiareXmlNode, self).__init__(
                master,
                columns=('name'),
                displaycolumns=(),
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

        # Allow horizontal scrolling
        # TODO width should be adjusted according to
        # number of decendents nodes.
        self.column("#0", width=600, stretch=False)

        self._property = None

        # item: xml_node
        self._values = {}

    def set_property(self, prperty_):
        self._property = prperty_
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
        item = self.insert(parent, 'end',
                           text=node.nodeName,
                           values=(node.nodeName),
                           tags=('element'))
        self._values[item] = node
        self.tag_bind('element', '<<TreeviewSelect>>', self._item_clicked)
        self._set_node_name(item)
        return item

    def _set_node_name(self, item):
        node = self._values[item]
        for n in node.childNodes:
            if n.nodeName == 'Name':
                node_text = self._get_node_text(n)
                if node_text is None:
                    node_test = 'Name?'
                text = self.item(item, 'text') + ' (' + node_text + ')'
                self.item(item, text=text)
                break

    def _get_node_text(self, node):
        for n in node.childNodes:
            if n.nodeName in ('#text'):
                return n.nodeValue

    def _item_clicked(self, event):
        sel = self.selection()
        item = sel[0] if sel else None
        if item is None:
            return

        name = self.set(item, 'name')
        print('*******') 
        print(name)
        if name not in NuntiareXmlNode._properties:
            NuntiareXmlNode._properties[name] = []
            class_ = getattr(nuntiare, name)
            elements = nuntiare.Element._get_element_list(class_)
            for key, value in elements.items():
                if (not value or value[0] == nuntiare.Element.ELEMENT
                        or value[0] == nuntiare.Element.EXPRESSION_LIST):
                    continue
                NuntiareXmlNode._properties[name].append(key)

        self._property.clear()

        for prop in NuntiareXmlNode._properties[name]:
            print(prop)
            self._property.add_property(prop, True)


class NuntiareProperty(ttk.Frame):
    def __init__(self, master):
        super(NuntiareProperty, self).__init__(master)
        self._properties = {}
        self._row_count = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

    def add_property(self, text, required):
        id_ = text + '_' + str(required)
        if id_ not in self._properties:            
            self._properties[id_] = [
                    ttk.Label(self, text=text),
                    PropertyItem(self, text, required),
                ]

        property_ = self._properties[id_]
        property_[0].grid(row=self._row_count, column=0, sticky='wens')
        property_[1].grid(row=self._row_count, column=1, sticky='wens')
        self._row_count += 1

    def clear(self):
        i = 1
        while i < 3:
            wgs = self.grid_slaves(column=i)
            for wg in wgs:
                wg.grid_forget()
            i += 1
        self._row_count = 0


class PropertyItem(ttk.Frame):
    def __init__(self, master, text, required):
        super(PropertyItem, self).__init__(master)

        entry = ttk.Entry(self)
        entry.grid(row=0, column=0, sticky='wens')

        self._text = text
        self._required = required
        self._value = None
        self._default = None

    def set_value(value, default):
        self._value = value
        self._default = default

    def get_value(self):
        if self._value:
            return self._value
        if not self._value and self._required and self._default:
            return self._default
