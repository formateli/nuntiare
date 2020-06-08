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
        self._last_item = None

        # item: xml_node
        self._values = {}

    def set_property(self, prperty_):
        self._property = prperty_
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
        item = self.insert(parent, 'end',
                           text=node.nodeName,
                           values=(node.nodeName),
                           tags=('element'))
        self._values[item] = node
        self.tag_bind('element', '<<TreeviewSelect>>', self._item_clicked)
        self._show_item_name(item)
        return item

    def _show_item_name(self, item):
        text = self._get_node_value(item, 'Name')
        if text is not None:
            text = self.item(item, 'text') + ' (' + text + ')'
            self.item(item, text=text)

    def _set_node_value(self, item, name, value):
        self._get_node_value(item, name, value)

    def _get_node_value(self, item, name, set_value=None):
        node = self._values[item]
        for n in node.childNodes:
            if n.nodeName == name:
                if set_value is None:
                    return self._get_node_text(n)
                else:
                    self._set_node_text(n, set_value)

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
        if name not in NuntiareXmlNode._properties:
            NuntiareXmlNode._properties[name] = []
            class_ = getattr(nuntiare, name)
            elements = nuntiare.Element._get_element_list(class_)
            for key, value in elements.items():
                if (not value or value[0] == nuntiare.Element.ELEMENT
                        or value[0] == nuntiare.Element.EXPRESSION_LIST):
                    continue
                NuntiareXmlNode._properties[name].append(key)
            NuntiareXmlNode._properties[name].sort()

        self._property.set_item(item)

        for prop in NuntiareXmlNode._properties[name]:
            property_ = self._property.add_property(prop, True)
            # Get the value, if any, in current node
            property_.set_value(self._get_node_value(item, prop), None)

    def _property_changed(self, master, property_):
        item = master.get_item()
        self._set_node_value(item, property_._text, property_.get_value())


class NuntiareProperty(ttk.Frame):
    def __init__(self, master):
        super(NuntiareProperty, self).__init__(master)
        self._properties = {}
        self._row_count = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self._item = None

        self._bind_callbacks = {
                'property_changed': [],
            }

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

    def bind(self, event, callback):
        if event in self._bind_callbacks:
            self._bind_callbacks[event].append(callback)
        else:
            super(NuntiareProperty, self).bind(event, callback)

    def _fire_event(self, event, property_):
        callbacks = self._bind_callbacks[event]
        for cb in callbacks:
            cb(self, property_)

    def _property_focusout(self, property_):
        self._fire_event('property_changed', property_)


class PropertyItem(ttk.Frame):
    def __init__(self, master, text, required):
        super(PropertyItem, self).__init__(master)

        self._entry = ttk.Entry(self)
        self._entry.grid(row=0, column=0, sticky='wens')

        self._text = text
        self._required = required
        self._value = None
        self._default = None

        self._bind_callbacks = {
                'property_focusout': [],
            }
        self.bind('<FocusOut>', self._focusout)

    def set_value(self, value, default):
        self._value = value
        self._default = default
        self._entry.delete(0, 'end')
        if value is not None:
            self._entry.insert(0, self._value)

    def get_value(self):
        if self._value:
            return self._value
        if not self._value and self._required and self._default:
            return self._default

    def bind(self, event, callback):
        if event in self._bind_callbacks:
            self._bind_callbacks[event].append(callback)
        else:
            super(PropertyItem, self).bind(event, callback)

    def _fire_event(self, event):
        callbacks = self._bind_callbacks[event]
        for cb in callbacks:
            cb(self)

    def _focusout(self, event):
        value = self._entry.get()
        if value != self._value:
            self._value = value
            self._fire_event('property_focusout')
