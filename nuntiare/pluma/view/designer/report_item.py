# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ..common.tools import get_size_px


class ReportItem:
    def __init__(self, treeview, tree_node):
        self._treeview = treeview
        self._item = tree_node
        self._parent = self._get_info('parent')
        self._section = self._get_info('section')
        self._canvas = None
        self._type = self._treeview.set(tree_node, 'name')

    def set_canvas_section(self, sections):
        if self._section == 'PageHeader':
            self._canvas = sections.get_section('header')
        elif self._section == 'PageFooter':
            self._canvas = sections.get_section('footer')
        elif self._section == 'Body':
            self._canvas = sections.get_section('body')

    def draw(self):
        get_node_value = self._treeview._get_node_value

        fill = 'blue'
        if self._type == 'Textbox':
            fill = 'red'

        x1 = get_size_px(
                get_node_value(self._item, 'Left', default='0px'))
        y1 = get_size_px(
                get_node_value(self._item, 'Top', default='0px'))
        x2 = x1 + get_size_px(
                get_node_value(self._item, 'Width', default='0px'))
        y2 = y1 + get_size_px(
                get_node_value(self._item, 'Height', default='0px'))

        obj = self._canvas.draw_rectangle_style(x1, y1, x2, y2, style)

        obj = self._canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
        self._canvas.add_object(obj, self)
        self._canvas.tag_bind(obj, '<1>', self._item_click)

    def _item_click(self, event):
        it = self._canvas.find_overlapping(
            event.x, event.y, event.x + 1, event.y + 1)[0]
        report_item = self._canvas.get_object(it)
        self._canvas.select_item(report_item._item)
        self._treeview.focus_set()
        self._treeview.see(report_item._item)
        self._treeview.focus(report_item._item)
        self._treeview.selection_set(report_item._item)

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
