# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import Menu
from tkinter import ttk


class MenuManager():
    def __init__(self, root, image_manager):
        self._menues = {}
        self._images = image_manager

        self._tool_bar = ttk.Frame(root,  height=25)
        self._tool_bar.grid(column=0, row=0, sticky='w')
        self._tool_bar.grid_rowconfigure(0, weight=1)
        self._tool_bar.grid_columnconfigure(0, weight=1)
        self._next_tb_id = 0
        self._tool_bars = {}

        self.new_menu('main', None, parent=root)

    def new_menu(self, name, parent_name, parent=None):
        if name in self._menues:
            raise Exception("Menu '{0}' already exists.".format(name))
        if parent is None:
            parent = self.get_menu(parent_name)
        menu = Menu(parent, tearoff=0)
        self._menues[name] = menu
        return menu

    def get_menu(self, name):
        if name not in self._menues:
            raise Exception("Menu '{0}' not found.".format(name))
        return self._menues[name]

    def add_command(self, menu_name, label, acc, command, image=None):
        menu = self.get_menu(menu_name)
        if image is not None:
            image = self._images.get_image(image)
        menu.add_command(
                label=label,
                accelerator=acc,
                command=command,
                image=image,
                compound='left',
                underline=0,
            )

    def add_separator(self, menu_name):
        menu = self.get_menu(menu_name)
        menu.add_separator()

    def add_cascade(self, label, parent_name, menu_name):
        parent = self.get_menu(parent_name)
        menu = self.get_menu(menu_name)
        parent.add_cascade(label=label, menu=menu)

    def add_toolbar(self, name):
        if name in self._tool_bars:
            raise Exception("Tool bar '{0}' already exists.".format(name))

        toolbar = ToolBar(self._tool_bar, self._next_tb_id, name)
        self._tool_bar.grid_columnconfigure(self._next_tb_id, weight=1)

        self._next_tb_id += 1
        self._tool_bars[name] = toolbar

    def get_toolbar(self, name):
        if name not in self._tool_bars:
            raise Exception("Toolbar '{0}' not found.".format(name))
        return self._tool_bars[name]

    def add_toolbar_item(self, toolbar_name, item_name, command, image):
        image = self._images.get_image(image)
        tb = self.get_toolbar(toolbar_name)
        tb.add_item(item_name, command, image)


class ToolBar(ttk.Frame):
    def __init__(self, parent, id_, name):
        super(ToolBar, self).__init__(parent,  height=25)
        self.id = id_
        self.name = name
        self._items = {}
        self.grid(column=id_, row=0, sticky='w')

    def add_item(self, item_name, command, image):
        if item_name in self._items:
            raise Exception(
                "Toolbar '{0}' already has an item '{1}'.".format(
                    self.name, item_name))
        btn = ttk.Button(self, image=image, command=command)
        btn.pack(side='left')
        self._items[item_name] = btn
