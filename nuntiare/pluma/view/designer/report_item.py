# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
import nuntiare.definition.element as nuntiare
from ..common.tools import get_size_px


class ReportItemAttribute:
    def __init__(self, name, treeview):
        self.name = name
        self._treeview = treeview
        self._meta = treeview._element_meta[name]
        self.item = None
        self.style = None

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        result = None

        if name not in self._meta:
            raise Exception(
                "Inavlid attribute '{0}' for '{1}'".format(
                    name, self.name)
                )

        # Find value in a treeview node
        if self.item is not None:
            result = self._treeview._get_node_value(
                self.item, name)

        # Find default value in Element Meta
        if result is None:
            result = self._meta[name].default

        if result is not None:
            if self._meta[name].type == nuntiare.Element.SIZE:
                if isinstance(result, int) or \
                        isinstance(result, float):
                    result = str(result) + 'pt'

        return result

    def set_style(self):
        self.style = ReportItemAttribute(
            'Style', self._treeview)
        self.style.set_tree_item(self._get_sub_item('Style'))

    def set_tree_item(self, item):
        if item is None:
            return
        self.item = item
        name = self._treeview.set(item, 'name')
        if name != self.name:
            raise Exception('Invalid name. {0} != {1}'.format(
                name, self.name))

    def _get_sub_item(self, name):
        items = self._treeview.get_children(self.item)
        for it in items:
            if self._treeview.set(it, 'name') == name:
                return it


class ReportItem(ReportItemAttribute):
    def __init__(self, name, canvas, tree_node, parent, meta):
        super(ReportItem, self).__init__(
                name, canvas._master._treeview)

        self.set_tree_item(tree_node)

        self._canvas = canvas
        self._parent = parent

        if self.name in nuntiare._REPORT_ITEMS:
            self.set_style()

    def update(self, name_changed):
        print(name_changed)
        obj = self._canvas.get_object_from_report_item(self)
        x1, y1, x2, y2 = self._canvas.coords(obj)
        self._canvas.coords(
            obj,
            get_size_px(self.Left),
            get_size_px(self.Top),
            get_size_px(self.Left) + get_size_px(self.Width),
            get_size_px(self.Top) + get_size_px(self.Height)
            )

    def _sum_parent(self, name):
        if self._parent is None:
            return 0
        return getattr(self._parent, name)

    def draw(self):
        fill = 'blue'
        if self.name == 'Textbox':
            fill = 'red'

        obj = self._canvas.create_rectangle(
                get_size_px(self.Left),
                get_size_px(self.Top),
                get_size_px(self.Left) + get_size_px(self.Width),
                get_size_px(self.Top) + get_size_px(self.Height),
                fill=fill)
        self._canvas.add_object(obj, self)
        self._canvas.tag_bind(obj, '<1>', self._item_click)

    def _item_click(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

#        it = self._canvas.find_overlapping(
#            event.x, event.y, event.x + 1, event.y + 1)

        it = self._canvas.find_overlapping(
            x, y, x + 1, y + 1)

        if not it:
            return
        it = it[-1]
        report_item = self._canvas.get_report_item_from_object(it)
        self._treeview.focus_set()
        self._treeview.see(report_item.item)
        self._treeview.focus(report_item.item)
        self._treeview.selection_set(report_item.item)

#    def _get_info(self, val):
#        itm = self._item
#        while True:
#            parent = self._treeview.parent(itm)
#            if not parent:
#                break
#            if val == 'section':
#                if self._treeview._values[parent][0].nodeName in (
#                        'PageHeader', 'PageFooter', 'Body'):
#                    return self._treeview._values[parent][0].nodeName
#            elif val == 'parent':
#                if self._treeview._values[parent][1] is not None:
#                    return parent
#            itm = parent
