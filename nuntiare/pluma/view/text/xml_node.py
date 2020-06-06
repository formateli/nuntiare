# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
from tkinter import ttk


class NuntiareXmlNode(ttk.Treeview):
    def __init__(self, master, xscrollcommand, yscrollcommand):
        super(NuntiareXmlNode, self).__init__(
                master,
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

    def parse(self, xml, is_file):
        if is_file:
            self._doc = minidom.parse(xml)
        else:
            self._doc = minidom.parseString(xml)
        root = self._doc.getElementsByTagName('Nuntiare')[0]
        item = self.insert('', 0, text='Report')
        self._get_nodes(root, item, 0)

    def _get_nodes(self, node, parent, index):
        for n in node.childNodes:
            if n.nodeName in ('#comment', '#text'):
                continue
            item = self.insert(parent, index + 1, text=n.nodeName)
            if n.nodeName == 'Name': 
                text = self.item(parent, 'text') + '(Name)'
                self.item(parent, text=text)
            self._get_nodes(n, item, index + 1)
