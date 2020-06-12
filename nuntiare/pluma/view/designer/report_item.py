# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
import nuntiare.definition.element as nuntiare
from ..common.tools import get_size_px


class ElementMixin:
    def __init__(self, name, treeview):
        self.name = name
        self._treeview = treeview
        self._meta = treeview._element_meta[name]
        self.item = None
        self.parent_item = None

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

    def update(self, name_changed):
        raise NotImplementedError('update method not implemented.')

    def set_tree_item(self, item):
        if item is None:
            return
        self.item = item
        name = self._treeview.set(item, 'name')
        if name != self.name:
            raise Exception('Invalid name. {0} != {1}'.format(
                name, self.name))
        self.parent_item = self._treeview.parent(self.item)


class Style(ElementMixin):
    def __init__(self, name, treeview):
        super(Style, self).__init__(name, treeview)
        self.Border = ElementMixin('Border', self._treeview)
        self.RightBorder = ElementMixin('RightBorder', self._treeview)
        self.LeftBorder = ElementMixin('LeftBorder', self._treeview)
        self.TopBorder = ElementMixin('TopBorder', self._treeview)
        self.BottomBorder = ElementMixin('BottomBorder', self._treeview)

    def update(self, name_changed, type_=None):
        if type_ is None:
            type_ = self.name
        parent = self._treeview._values[self.parent_item][1]
        parent.update(name_changed, type_=type_)


class ElementStyle(ElementMixin):
    def __init__(self, name, treeview):
        super(ElementStyle, self).__init__(name, treeview)
        self.Style = Style('Style', self._treeview)


class ReportItem(ElementStyle):
    def __init__(self, name, canvas, tree_node, parent, meta):
        super(ReportItem, self).__init__(
                name, canvas._master._treeview)
        self._canvas = canvas
        self._parent = parent
        self._rec = None
        self._txt = None
        self.set_tree_item(tree_node)

    def update(self, name_changed, type_=None):
        if type_ == 'Style':
            if name_changed == 'BackgroundColor':
                self._canvas.itemconfig(
                    self._rec, fill=self.Style.BackgroundColor)
            elif name_changed == 'Color':
                self._canvas.itemconfig(
                    self._txt, fill=self.Style.Color)
        else:
            if name_changed in ('Left', 'Top', 'Width', 'Height'):
                x1, y1, x2, y2 = self._canvas.coords(self._rec)
                self._canvas.coords(
                    self._rec,
                    get_size_px(self.Left),
                    get_size_px(self.Top),
                    get_size_px(self.Left) + get_size_px(self.Width),
                    get_size_px(self.Top) + get_size_px(self.Height)
                    )

    def _sum_parent(self, name):
        if self._parent is None:
            return 0
        return getattr(self._parent, name)

    def create(self):
        fill = 'white'
        outline = None
        if self.Style.item:
            fill = self.Style.BackgroundColor
            if fill is None: fill = 'white'

        self._rec = self._canvas.create_rectangle(
            get_size_px(self.Left),
            get_size_px(self.Top),
            get_size_px(self.Left) + get_size_px(self.Width),
            get_size_px(self.Top) + get_size_px(self.Height),
            fill=fill, outline=outline, width=0
            )
        self._add_object(self._rec)

        if self.name == 'Textbox':
            self._txt = self._canvas.create_text(
                get_size_px(self.Left),
                get_size_px(self.Top),
                anchor='nw',
                width=get_size_px(self.Width),
                fill=self.Style.Color,
                text=self.Value
                )
            self._add_object(self._txt)

    def _add_object(self, obj):
        self._canvas.add_object(obj, self)
        self._canvas.tag_bind(obj, '<1>', self._object_click)

    def _object_click(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)
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
