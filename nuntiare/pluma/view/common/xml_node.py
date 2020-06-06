# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
from tkinter import ttk
from nuntiare.definition.element import (
        _ELEMENT_CLASSES, _EXPRESSION_LIST_CLASSES)


class NuntiareXmlNode(ttk.Treeview):
    def __init__(self, master, xscrollcommand, yscrollcommand):
        super(NuntiareXmlNode, self).__init__(
                master,
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

        # item: xml_node
        self._values = {}

    def parse(self, xml, is_file):
        if is_file:
            self._doc = minidom.parse(xml)
        else:
            self._doc = minidom.parseString(xml)
        root = self._doc.getElementsByTagName('Nuntiare')[0]
        item = self._add_node_element('', root, -1)
        #item = self.insert('', 0, text='Report')
        #self._values[item] = root
        self._get_nodes(root, item, 0)

    def _get_nodes(self, node, parent, index):
        for n in node.childNodes:
            if n.nodeName in ('#comment', '#text'):
                continue
            if (n.nodeName in _ELEMENT_CLASSES
                    or n.nodeName in _EXPRESSION_LIST_CLASSES):
                item = self.insert(
                    parent, index + 1, text=n.nodeName)
                self._values[item] = n
                self._set_node_name(item)
                self._get_nodes(n, item, index + 1)

    def _add_node_element(self, parent, node, index):
        item = self.insert(parent, index + 1, text=node.nodeName)
        self._values[item] = node
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
