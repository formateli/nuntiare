# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from nuntiare.definition.expression import Size


class ReportItem:
    def __init__(self, treeview, tree_node):
        self._treeview = treeview
        self._item = tree_node
        self._parent = self._get_info('parent')
        self._section = self._get_info('section')
        self._canvas = None
        self._ppi = None

    def set_canvas_section(self, sections):
        if self._section == 'PageHeader':
            self._canvas = sections.header
        elif self._section == 'PageFooter':
            self._canvas = sections.footer
        elif self._section == 'Body':
            self._canvas = sections.body
        self._ppi = self._canvas.winfo_pixels('1i')

    def draw(self):
        get_node_value = self._treeview._get_node_value

        self._canvas.create_rectangle(
            self._get_size(
                get_node_value(self._item, 'Top', default='0px')),
            self._get_size(
                get_node_value(self._item, 'Left', default='0px')),
            self._get_size(
                get_node_value(self._item, 'width', default='0px')),
            self._get_size(
                get_node_value(self._item, 'height', default='0px')),
            fill="blue")

    def _get_size(self, value):
        res = Size.split_size_string(value)
        if res is None:
            return
        return Size.convert_to_pixel(float(res[0]), res[1], self._ppi)

    def _get_info(self, val):
        itm = self._item
        while True:
            parent = self._treeview.parent(itm)
            if not parent:
                break
            if val == 'section':
                if self._treeview._values[parent][0].nodeName in (
                        'PageHeader', 'PageFooter', 'Body'):
                    return self._treeview._values[parent][0].nodeName
            elif val == 'parent':
                if self._treeview._values[parent][1] is not None:
                    return parent
            itm = parent
