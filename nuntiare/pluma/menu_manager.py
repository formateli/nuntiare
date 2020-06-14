# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from tkinter import Menu
from tkinter import DISABLED
from tkinter import ttk
from .materialtheme import ImageManager


class MenuManager():

    _menues = {}
    _image_size = '16x16'

    def __init__(self, root):
        pass

    @classmethod
    def new_menu(cls, name, parent_name, master=None, image_size=None):
        if name in cls._menues:
            raise Exception("Menu '{0}' already exists.".format(name))
        if master is None:
            master = cls.get_menu(parent_name)
        menu = PlumaMenu(master, name, image_size)
        cls._menues[name] = menu
        return menu

    @classmethod
    def get_menu(cls, name):
        if name not in cls._menues:
            raise Exception("Menu '{0}' not found.".format(name))
        return cls._menues[name]

    @classmethod
    def add_command(cls, menu_name, item_name,
                    label, acc, command,
                    image=None, state=DISABLED):
        menu = cls.get_menu(menu_name)
        if image is not None:
            size = cls._image_size
            if menu._image_size is not None:
                size = menu._image_size
            image = ImageManager.get_image(image, size=size)
        menu.add_command(item_name, label, acc, command, image, state)

    @classmethod
    def set_menu_command_state(
                cls, menu_name, item_name, state):
        menu = cls.get_menu(menu_name)
        menu.set_command_state(item_name, state)

    @classmethod
    def add_separator(cls, menu_name):
        menu = cls.get_menu(menu_name)
        menu.add_separator()

    @classmethod
    def add_cascade(cls, label, parent_name, menu_name):
        parent = cls.get_menu(parent_name)
        menu = cls.get_menu(menu_name)
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

    def add_toolbar_item(
            self, toolbar_name, item_name,
            command, image, state=DISABLED):
        image = self._images.get_image(image)
        tb = self.get_toolbar(toolbar_name)
        tb.add_item(item_name, command, image, state)

    def get_toolbar_item(self, toolbar_name, item_name):
        tb = self.get_toolbar(toolbar_name)
        item = tb.get_item(item_name)
        return item

    def set_toolbar_item_state(
            self, toolbar_name, item_name, state):
        item = self.get_toolbar_item(toolbar_name, item_name)
        item['state'] = state

    def linK_menu_toolbar_item(
                self, link_name,
                menu_name, menu_item_name,
                toolbar_name, toolbar_item_name):
        if link_name in self._links:
            raise Exception("Link '{0}' already exists.".format(link_name))
        self._links[link_name] = {
                'menu': self.get_menu(menu_name),
                'menu_item': menu_item_name,
                'toolbar_item': self.get_toolbar_item(
                        toolbar_name, toolbar_item_name),
            }

    def link_set_state(self, link_name, state):
        if link_name not in self._links:
            raise Exception("Link '{0}' not found.".format(link_name))
        lnk = self._links[link_name]
        lnk['menu'].set_command_state(
            lnk['menu_item'], state)
        lnk['toolbar_item']['state'] = state


class PlumaMenu(Menu):
    def __init__(self, parent, name, image_size=None):
        super(PlumaMenu, self).__init__(parent, tearoff=0)
        self.name = name
        self._next_val = 0
        self._items = {}
        self._image_size = image_size

    def add_command(self, item_name, label, acc, command, image, state):
        if item_name in self._items:
            raise Exception(
                "Menu '{0}' already has an item '{1}'.".format(
                    self.name, item_name))
        self.insert_command(
                self._next_val,
                label=label,
                accelerator=acc,
                command=command,
                image=image,
                state=state,
                compound='left',
                underline=0,
            )
        self._items[item_name] = self._next_val
        self._next_val += 1

    def set_command_state(self, item_name, state):
        if item_name not in self._items:
            raise Exception(
                "Menu '{0}' item '{1}' not found.".format(
                    self.name, item_name))
        self.entryconfig(self._items[item_name], state=state)

    def add_separator(self):
        self.insert_separator(self._next_val)
        self._next_val += 1

    def add_cascade(self, label, menu):
        self.insert_cascade(
            self._next_val, label=label, menu=menu)
        self._next_val += 1


class ToolBar(ttk.Frame):
    def __init__(self, parent, id_, name):
        super(ToolBar, self).__init__(parent,  height=25)
        self.id = id_
        self.name = name
        self._items = {}
        self.grid(column=id_, row=0, sticky='w')

    def add_item(self, item_name, command, image, state):
        if item_name in self._items:
            raise Exception(
                "Toolbar '{0}' already has an item '{1}'.".format(
                    self.name, item_name))
        btn = ttk.Button(self, image=image, command=command, state=state)
        btn.pack(side='left')
        self._items[item_name] = btn

    def get_item(self, item_name):
        if item_name not in self._items:
            raise Exception(
                "Toolbar '{0}' item '{1}' not found.".format(
                    self.name, item_name))
        return self._items[item_name]
