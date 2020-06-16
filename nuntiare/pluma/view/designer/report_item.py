# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
#import tkinter as tk
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
        self.last_is_default = False

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        result = None
        self.last_is_default = False

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
            self.last_is_default = True

        if result is not None:
            if self._meta[name].type == nuntiare.Element.SIZE:
                if isinstance(result, int) or \
                        isinstance(result, float):
                    result = str(result) + 'pt'

        return result

    def update(self, name_changed, type_=None):
        raise NotImplementedError(
            'update method not implemented by {}'.format(
                self.__class__.__name__))

    def set_tree_item(self, item):
        if item is None:
            return
        self.item = item
        if self._treeview is None:
            return
        name = self._treeview.set(item, 'name')
        if name != self.name:
            raise Exception('Invalid name. {0} != {1}'.format(
                name, self.name))
        self.parent_item = self._treeview.parent(self.item)


class UpdateParentElement(ElementMixin):
    def __init__(self, name, treeview):
        super(UpdateParentElement, self).__init__(name, treeview)

    def update(self, name_changed, type_=None):
        if type_ is None:
            type_ = self.name
        parent = self._treeview._values[self.parent_item][1]
        parent.update(name_changed, type_=type_)


class Style(UpdateParentElement):
    def __init__(self, name, treeview):
        super(Style, self).__init__(name, treeview)
        self.Border = UpdateParentElement(
                'Border', self._treeview)
        self.RightBorder = UpdateParentElement(
                'RightBorder', self._treeview)
        self.LeftBorder = UpdateParentElement(
                'LeftBorder', self._treeview)
        self.TopBorder = UpdateParentElement(
                'TopBorder', self._treeview)
        self.BottomBorder = UpdateParentElement(
                'BottomBorder', self._treeview)

    def get_borders(self):
        result = {
            'TopBorder': {},
            'BottomBorder': {},
            'LeftBorder': {},
            'RightBorder': {},
            }

        values = ['Color', 'BorderStyle', 'Width']

        for key, res in result.items():
            for value in values:
                res[value] = self._get_border_value(key, value)

        equal = True
        for value in values:
            last = None
            for key in result.keys():
                res = result[key][value]
                if last is None:
                    last = res
                else:
                    if last != res:
                        equal = False
                        break

        result['equal'] = equal
        return result

    def _get_border_value(self, element, name):
        el = getattr(self, element)
        result = getattr(el, name)
        if self.last_is_default:
            result = getattr(self.Border, name)
        return result


class ElementStyle(ElementMixin):
    def __init__(self, name, treeview):
        super(ElementStyle, self).__init__(name, treeview)
        self.Style = Style('Style', self._treeview)


class ReportItem(ElementStyle):
    def __init__(self, name, canvas, treeview, parent_ri):
        super(ReportItem, self).__init__(
                name, treeview)
        self._canvas = canvas
        self._parent_ri = parent_ri
        self._children_ri = []
        self._rec = None
        self._txt = None

        if parent_ri is not None:
            if parent_ri.name in ('Body', 'PageHeader', 'PageFooter'):
                parent_ri = None
            else:
                parent_ri._children_ri.append(self)

    def get_top(self):
        result = 0
        if self._parent_ri:
            print(self._parent_ri.Name)
            result += self._parent_ri.get_top()
        result += get_size_px(self.Top)
        return result

    def get_left(self):
        result = 0
        if self._parent_ri:
            print(self._parent_ri.Name)
            result += self._parent_ri.get_left()
        result += get_size_px(self.Left)
        return result

    def remove_all(self):
        self._canvas.delete(self._txt)
        self._canvas.delete(self._rec)
        self._canvas.remove_report_items(self)

    def update(self, name_changed, type_=None):
        if self._canvas is None:
            return

        opts_rec = {}
        opts_txt = {}

        if type_ == 'Style':
            if name_changed == 'BackgroundColor':
                opts_rec['fill'] = self.Style.BackgroundColor

            elif name_changed == 'Color':
                opts_txt['fill'] = self.Style.Color

            elif name_changed in ('FontFamily', 'FontSize',
                    'FontWeight', 'TextDecoration', 'FontStyle'):
                opts_txt['font'] = self._get_font(self.Style)

        if type_ in ('Border', 'RightBorder',
                'LeftBorder', 'TopBorder', 'BottomBorder'):
            borders = self.Style.get_borders()
            if borders['equal']:
                opts_rec['outline'] = borders['TopBorder']['Color']
                opts_rec['width'] = get_size_px(borders['TopBorder']['Width'])
                bs = borders['TopBorder']['BorderStyle']
                if bs == 'None':
                    opts_rec['width'] = 0
                    opts_rec['outline'] = None

        else:
            if name_changed in ('Left', 'Top', 'Width', 'Height'):
                left = self.get_left()
                top = self.get_top()
                x1, y1, x2, y2 = self._canvas.coords(self._rec)
                self._canvas.coords(
                    self._rec, left, top,
                    left + get_size_px(self.Width),
                    top + get_size_px(self.Height)
                    )

                #if self._txt is not None:
                #    x1, y1, x2, y2 = self._canvas.coords(self._txt)
                #    self._canvas.coords(
                #        self._txt, left, top,
                #        left + get_size_px(self.Width),
                #        top + get_size_px(self.Height)
                #        )

                if name_changed in ('Left', 'Top'):
                    for ri in self._children_ri:
                        print('Updating child ' + ri.name)
                        ri.update(name_changed, type_)

            elif name_changed == 'Value':
                opts_txt['text'] = self.Value

        if opts_rec:
            self._canvas.itemconfig(self._rec, **opts_rec)
        elif opts_txt:
            self._canvas.itemconfig(self._txt, **opts_txt)

    def _sum_parent(self, name):
        if self._parent is None:
            return 0
        return getattr(self._parent, name)

    def create(self):
        if self._canvas is None:
            return

        fill = self.Style.BackgroundColor
        if fill is None: fill = 'white'

        outline = None
        border_width = 0
        borders = self.Style.get_borders()
        if borders['equal']:
            outline = borders['TopBorder']['Color']
            bs = borders['TopBorder']['BorderStyle']
            if bs != 'None':
                border_width = get_size_px(borders['TopBorder']['Width'])

        left = self.get_left()
        top = self.get_top()

        self._rec = self._canvas.create_rectangle(
            left, top,
            left + get_size_px(self.Width),
            top + get_size_px(self.Height),
            fill=fill, outline=outline, width=border_width
            )
        self._add_object(self._rec)

        if self.name == 'Textbox':
            self._txt = self._canvas.create_text(
                left, top, anchor='nw',
                width=get_size_px(self.Width),
                font=self._get_font(self.Style),
                fill=self.Style.Color,
                text=self.Value
                )
            self._add_object(self._txt)

    @staticmethod
    def _get_font(style):
        slant = style.FontStyle.lower()
        if slant != 'italic':
            slant = 'roman'

        underline = 0
        overstrike = 0
        if style.TextDecoration.lower() == 'underline':
            underline = 1
        if style.TextDecoration.lower() == 'LineThrough':
            overstrike = 1

        font = tk.font.Font(
            family=style.FontFamily,
            size=-get_size_px(style.FontSize),
            weight=style.FontWeight.lower(),
            slant=slant,
            underline=underline,
            overstrike=overstrike
            )
        return font

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
