# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ..common.tools import get_size_px


class ReportItem:
    def __init__(self, canvas, tree_node, parent, type_):
        self._canvas = canvas
        self._treeview = canvas._master._treeview
        self.item = tree_node
        self._parent = parent
        self._type = type_

        self.left = 0
        self.top = 0
        self.width = 0
        self.height = 0

    def set_size(self, left, top, width, height):
        self.left = left + self._sum_parent('left')
        self.top = top + self._sum_parent('top')
        self.width = width
        self.height = height

    def _sum_parent(self, name):
        if self._parent is None:
            return 0
        return getattr(self._parent, name)

    def draw(self):
        fill = 'blue'
        if self._type == 'Textbox':
            fill = 'red'
        obj = self._canvas.create_rectangle(
                self.left,
                self.top, 
                self.left + self.width,
                self.top + self.height,
                fill=fill)
        self._canvas.add_object(obj, self)
        self._canvas.tag_bind(obj, '<1>', self._item_click)

    def _item_click(self, event):
        it = self._canvas.find_overlapping(
            event.x, event.y, event.x + 1, event.y + 1)[0]
        report_item = self._canvas.get_object(it)
        #self._canvas.select_item(report_item._item)
        self._treeview.focus_set()
        self._treeview.see(report_item.item)
        self._treeview.focus(report_item.item)
        self._treeview.selection_set(report_item.item)

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
