# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import os
from .image_manager import ImageManager
from .menu_manager import MenuManager
from .widget import UITabsObserver, UITabs
from .highlight import Highlight
from .view import NuntiareView

DIR = os.path.dirname(os.path.realpath(__file__))


class Pluma(UITabsObserver):
    def __init__(self):
        self.root = Tk()
        self.root.title("Pluma - Nuntiare Report Designer")
        self.root.geometry('500x500')

        self.highlight = Highlight()
        self.highlight.load_syntax_files()

        ICON = os.path.join(DIR, 'images', '24x24')

        image_manager = ImageManager()
        image_manager.add_images([
                ICON + '/new_file.png',
                ICON + '/open_file.png',
                ICON + '/save.png',
                ICON + '/exit.png',
                ICON + '/undo.png',
                ICON + '/redo.png',
            ])

        # menu

        self.menu = MenuManager(self.root, image_manager)

        self.menu.new_menu('file', 'main')
        self.menu.add_command(
            'file', 'new', 'New', 'Ctrl+N', self.new_file,
            image='new_file', state=NORMAL)
        self.menu.add_command(
            'file', 'open', 'Open', 'Ctrl+O', self.open_file,
            image='open_file', state=NORMAL)
        self.menu.add_command(
            'file', 'save', 'Save', 'Ctrl+S', self.save, image='save')
        self.menu.add_separator('file')
        self.menu.add_command(
            'file', 'exit', 'Exit', 'Alt+F4', self.exit_pluma,
            image='exit', state=NORMAL)

        self.menu.add_cascade('File', 'main', 'file')

        self.menu.new_menu('edit', 'main')
        self.menu.add_command(
            'edit', 'undo', 'Undo', 'Ctrl+Z', self.undo, image='undo')
        self.menu.add_command(
            'edit', 'redo', 'Redo', 'Ctrl+Y', self.redo, image='redo')
        self.menu.add_separator('edit')
        self.menu.add_command(
            'edit', 'copy', 'Copy', 'Ctrl+C', self.copy)
        self.menu.add_command(
            'edit', 'paste', 'Paste', 'Ctrl+V', self.paste)
        self.menu.add_command(
            'edit', 'cut', 'Cut', 'Ctrl+X', self.cut)
        self.menu.add_separator('edit')
        self.menu.add_command(
            'edit', 'select_all', 'Select All', 'Ctrl+A', self.select_all)

        self.menu.add_cascade('Edit', 'main', 'edit')

        self.root.config(menu=self.menu.get_menu('main'))
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # toolbar

        self.menu.add_toolbar('file')
        self.menu.add_toolbar_item('file', 'new', self.new_file, 'new_file', NORMAL)
        self.menu.add_toolbar_item('file', 'open', self.open_file, 'open_file', NORMAL)
        self.menu.add_toolbar_item('file', 'save', self.save, 'save')

        self.menu.add_toolbar('undo_redo')
        self.menu.add_toolbar_item('undo_redo', 'undo', self.undo, 'undo')
        self.menu.add_toolbar_item('undo_redo', 'redo', self.redo, 'redo')

        # link menu and toolbar items

        self.menu.linK_menu_toolbar_item('save', 
            'file', 'save', 'file', 'save')

        self.menu.linK_menu_toolbar_item('undo', 
            'edit', 'undo', 'undo_redo', 'undo')
        self.menu.linK_menu_toolbar_item('redo', 
            'edit', 'redo', 'undo_redo', 'redo')

        # tabs

        self.tab_count = 1
        self.tabs = UITabs(self.root, self)
        self.tabs.grid(column=0, row=1, sticky='ew')

        self.views = {}
        self.current_view = None

        self.root.mainloop()

    def handle_addtab(self, tabs, file_name=None):
        tabs.add(tabid=self.tab_count,
            title='Untitled ' + str(self.tab_count),
            dirty=True)
        view = NuntiareView(self.tab_count, self, tabs, file_name)
        view.grid(column=0, row=2, sticky='nwes')
        self.views[self.tab_count] = view
        self.current_view = view
        self.tab_count += 1

        view.xml.widget.bind('<Control-c>', self.copy)
        view.xml.widget.bind('<Control-C>', self.copy)
        view.xml.widget.bind('<Control-v>', self.paste)
        view.xml.widget.bind('<Control-V>', self.paste)
        view.xml.widget.bind('<Control-x>', self.cut)
        view.xml.widget.bind('<Control-X>', self.cut)

    def handle_closetab(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()
            self.views[tabid].destroy()
            del self.views[tabid]
        tabs.remove(tabid)

        if len(tabs.tabs) == 0:
            self.current_view = None
            self._verify_undo_redo()

    def tab_deselected(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()

    def tab_selected(self, tabs, tabid):
        if tabid in self.views: 
            view = self.views[tabid]
            view.grid(column=0, row=2, sticky='nwes')
            self.current_view = view
            self._verify_undo_redo()

    def new_file(self, event=None):
        self.handle_addtab(self.tabs)

    def open_file(self, event=None):
        input_file_name = tkinter.filedialog.askopenfilename(
                    defaultextension=".txt",
                    filetypes=[("All Files", "*.*"), ("Xml Documents", "*.xml")])
        if input_file_name:
            self.handle_addtab(self.tabs, input_file_name)

    def copy(self, event=None):
        view = self.current_view
        copypaste = view.copypaste
        if view and \
                view.current_paned_view.type == 'xml':
            txt = view.xml.widget.get(SEL_FIRST, SEL_LAST)
            if txt is not None:
                copypaste.add_copy(txt)
                return txt
        return 'break'

    def paste(self, event=None):
        view = self.current_view
        copypaste = view.copypaste
        if view and \
                view.current_paned_view.type == 'xml':
            txt = copypaste.get_paste()
            if txt is not None:
                view.xml.widget.insert(
                    INSERT, txt[0])
        return 'break'

    def cut(self, event=None):
        txt = self.copy()
        if txt is not None:
            self.current_view.xml.widget.delete(SEL_FIRST, SEL_LAST)
        return 'break'

    def select_all(self, event=None):
        view = self.current_view
        if view and \
                view.current_paned_view.type == 'xml':
            view.xml.widget.tag_add('sel', '1.0', 'end')

    def save(self, event=None):
        pass

    def save_as(self, event=None):
        pass

    def undo(self, event=None):
        view = self.current_view
        memento = view.memento
        if memento.is_undo_possible():
            history = memento.get_undo_memento()
            if history.type == 'inserted':
                view.xml.widget.delete(
                    history.index_start(), history.index_end(), True)
            elif history.type == 'deleted':
                view.xml.widget.insert(
                    history.index_start(), history.text, True)

    def redo(self, event=None):
        view = self.current_view
        memento = view.memento
        if memento.is_redo_possible():
            history = memento.get_redo_memento()
            if history.type == 'inserted':
                view.xml.widget.insert(
                    history.index_start(), history.text, True)
            elif history.type == 'deleted':
                view.xml.widget.delete(
                    history.index_start(), history.index_end(), True)

    def _verify_undo_redo(self):
        view = self.current_view
        undo_state = DISABLED
        redo_state = DISABLED
        if view is not None:
            memento = view.memento
            if memento.is_undo_possible():
                undo_state = NORMAL
            if memento.is_redo_possible():
                redo_state = NORMAL

        self.menu.link_set_state('undo', undo_state)
        self.menu.link_set_state('redo', redo_state)

    def exit_pluma(self, event=None):
        if tkinter.messagebox.askokcancel("Quit?",
                "Do you want to QUIT for sure?\n Make sure you've saved your current work."):
            self.root.destroy()

    def run(self):
        self.root.mainloop()
        try:
            self.root.destroy()
        except:
            pass
