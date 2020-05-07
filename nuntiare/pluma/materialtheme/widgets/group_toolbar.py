# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from . import WidgetThemeMixin
from ..theme import Theme


class GroupToolBar(ttk.Frame):

    _style_class = None

    def __init__(self, root,  height=25, **kwargs):
        self._get_style()
        if 'style' not in kwargs:
            kwargs['style'] = GroupToolBar._style_class + '.TFrame'
        super(GroupToolBar, self).__init__(root, height=height, **kwargs)
        self.height = height
        self.grid_propagate(0)  # force height
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._next_tb_id = 0
        self._tool_bars = {}

    def add_toolbar(self, name, after=None):
        if name in self._tool_bars:
            raise Exception("Toolbar '{0}' already exists.".format(name))
        if after is not None:
            after = self.get_toolbar(after)

        id_ = self._next_tb_id
        if after is not None:
            i = after.id
            id_ = i + 1
            for _, tb in self._tool_bars.items():
                if tb.id > i:
                    tb.change_id(tb.id + 1)

        toolbar = _ToolBar(
                self, id_, name,
                GroupToolBar._style_class + '.TFrame')

        self.grid_columnconfigure(self._next_tb_id, weight=1)

        self._tool_bars[name] = toolbar
        self._next_tb_id += 1

    def get_toolbar(self, name):
        if name not in self._tool_bars:
            raise Exception("Toolbar '{0}' not found.".format(name))
        return self._tool_bars[name]

    def add_toolbar_item(self, toolbar_name, item_name,
                         command, image_name, image_size='24x24',
                         state=tk.NORMAL, side='left'):
        tb = self.get_toolbar(toolbar_name)
        item = tb.add_item(
                item_name, command,
                image_name, image_size, state, side,
                GroupToolBar._style_class + '.TButton')
        return item

    def show(self, toolbar_name, show):
        tb = self.get_toolbar(toolbar_name)
        tb.show(show)

    def enable(self, toolbar_name, item, enable):
        tb = self.get_toolbar(toolbar_name)
        tb.enable(item, enable)

    def set_command(self, toolbar_name, item, command):
        tb = self.get_toolbar(toolbar_name)
        tb.set_command(item, command)

    @classmethod
    def _get_style(cls, force=False):
        if GroupToolBar._style_class is not None and not force:
            return

        style = ttk.Style()
        GroupToolBar._style_class = 'GroupToolBar'

        st = ['TFrame', 'TButton']

        for key in st:
            name = GroupToolBar._style_class + '.' + key
            opts = {
                    'background': style.lookup(key, 'foreground'),
                    'foreground': style.lookup(key, 'background'),
                }
            cs = style.configure(name)
            if cs is None:
                style.configure(name, **opts)
            else:
                add_opts = {}
                for opt, value in opts.items():
                    if not style.lookup(name, opt):
                        add_opts[opt] = value
                if add_opts:
                    style.configure(name, **add_opts)


class _ToolBar(ttk.Frame):
    def __init__(self, parent, id_, name, style):
        super(_ToolBar, self).__init__(parent,
                                       height=parent.height,
                                       style=style)
        self.id = id_
        self.name = name
        self._items = {}
        self.grid(column=id_, row=0, sticky='we')

    def change_id(self, new_id):
        self.grid_forget()
        self.id = new_id
        self.grid(column=new_id, row=0, sticky='we')

    def show(self, show):
        if show:
            self.grid()
        else:
            self.grid_remove()

    def enable(self, item_name, enable):
        item = self._items[item_name]
        if enable:
            state = ['!disabled']
        else:
            state = ['disabled']
        item.state(state)

    def set_command(self, item_name, command):
        item = self._items[item_name]
        item.config(command=command)

    def add_item(self, item_name, command,
                 image_name, image_size, state, side, style):
        if item_name in self._items:
            raise Exception(
                "Toolbar '{0}' already has an item '{1}'.".format(
                    self.name, item_name))
        item = _ToolBarItem(
                self, item_name, image_name,
                image_size, command, state, side, style)
        self._items[item_name] = item
        return item

    def get_item(self, item_name):
        if item_name not in self._items:
            raise Exception(
                "Toolbar '{0}' item '{1}' not found.".format(
                    self.name, item_name))
        return self._items[item_name]


class _ToolBarItem(ttk.Button):
    def __init__(self, master, name, image_name, image_size,
                 command, state, side, style):
        if Theme._curr_theme:
            color = Theme._curr_theme.config['primary_text_color']
        else:
            color = 'black'
        image = Theme._images.get_image(
            image_name, size=image_size, color=color)

        super(_ToolBarItem, self).__init__(
                master, image=image, command=command,
                state=state, style=style)
        self.name = name
        self._image_name = image_name
        self._image_size = image_size
        self.pack(side=side)

    def set_image_color(self, color):
        image = Theme._images.get_image(
            self._image_name, size=self._image_size, color=color)
        self.config(image=image)


class GroupToolBarTheme(GroupToolBar, WidgetThemeMixin):
    def __init__(self, root,  height=25, **kwargs):
        GroupToolBar.__init__(self, root, height=height, **kwargs)
        WidgetThemeMixin.__init__(self)

    def _on_theme_changed(self, theme):
        # TODO see onoffbutton
        self._get_style(force=True)
        if theme is None:
            style = ttk.Style()
            color = style.lookup(
                    self._style_class + '.TButton', 'foreground')
        else:
            color = theme.config['primary_text_color']

        for _, toolbar in self._tool_bars.items():
            for _, item in toolbar._items.items():
                item.set_image_color(color)
