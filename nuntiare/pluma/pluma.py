# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
import os
from .image_manager import ImageManager
from .menu_manager import MenuManager
from .widget import UITabsObserver, UITabs, TextEvent
from .memento import MementoCaretaker

DIR = os.path.dirname(os.path.realpath(__file__))


class PanedView(ttk.PanedWindow):
    def __init__(self, id_, pluma, view, tabs, file_name):
        self.id = id_
        self.pluma = pluma
        self.view = view
        self.widget = None
        self.tabs = tabs
        self.file_name = file_name
        self.memento = MementoCaretaker()

        super(PanedView, self).__init__(view.notebook, orient=HORIZONTAL)
        self.pack(fill=BOTH, expand=1)

        self.left_frame = ttk.Frame(view.notebook)
        self.left_frame.pack(fill=BOTH, expand=1)
        self.add(self.left_frame)

        # Horizontal (x) Scroll bar
        self.xscrollbar = ttk.Scrollbar(self.left_frame, orient=HORIZONTAL)
        self.xscrollbar.pack(side=BOTTOM, fill=X)

        # Vertical (y) Scroll Bar
        self.yscrollbar = ttk.Scrollbar(self.left_frame)
        self.yscrollbar.pack(side=RIGHT, fill=Y)

        self.right_frame = ttk.Frame(view.notebook)
        self.right_frame.pack(fill=BOTH, expand=1)
        self.add(self.right_frame)

    def clear_memento(self):
        self.memento.clear()
        self.pluma.menu.set_toolbar_item_state(
            'undo_redo', 'undo', DISABLED)
        self.pluma.menu.set_toolbar_item_state(
            'undo_redo', 'redo', DISABLED)


class DesignEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs, file_name):
        super(DesignEditor, self).__init__(
            id_, pluma, view, tabs, file_name)

        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class XmlEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs, file_name):
        super(XmlEditor, self).__init__(
            id_, pluma, view, tabs, file_name)

        self.widget = TextEvent(self.left_frame,
                xscrollcommand=self.xscrollbar.set,
                yscrollcommand=self.yscrollbar.set)
        self.widget.pack(fill=BOTH, expand=1)

        self.xscrollbar.config(command=self.widget.xview)
        self.yscrollbar.config(command=self.widget.yview)

        self.widget.bind("<<TextModified>>", self.onTextModified)

        self.new_file()

    def onTextModified(self, event):
        if not self.widget.is_undo_redo:
            self.memento.insert_memento(
                event.widget.text_changed_info.copy())
        self.widget.is_undo_redo = None
        self._update_undo_redo()
        self.pluma.menu.link_set_state('save', NORMAL)

    def _update_undo_redo(self):
        self._update_undo_redo_item(
            'undo', self.memento.is_undo_possible())
        self._update_undo_redo_item(
            'redo', self.memento.is_redo_possible())

    def _update_undo_redo_item(self, name, possible):
        if possible:
            state = NORMAL
        else:
            state = DISABLED
        #self.pluma.menu.set_toolbar_item_state(
        #    'undo_redo', name, state)
        self.pluma.menu.link_set_state(name, state)

    def new_file(self):
        self.widget.delete(1.0, END)
        if self.file_name is None:
            self.widget.insert('1.0', self.new_snipet(), True)
            state = NORMAL
        else:
            self.get_file_content()
            self.tabs.set_title(self.id, self.file_name)
            self.tabs.set_dirty(self.id, False)
            self.tabs.set_tooltip(self.id, self.file_name)
            state = DISABLED
        self.pluma.menu.link_set_state('save', state)
        self.clear_memento()

    def new_snipet(self):
        xml = '''<?xml version="1.0" ?>
<Nuntiare>
</Nuntiare>'''
        return xml

    def get_file_content(self):
        with open(self.file_name) as file_:
            self.widget.insert(1.0, file_.read(), True)


class RunView(PanedView):
    def __init__(self, id_, pluma, view, tabs, file_name):
        super(RunView, self).__init__(
            id_, pluma, view, tabs, file_name)

        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class NuntiareView(ttk.Frame):
    def __init__(self, id_, pluma, tabs, file_name):
        super(NuntiareView, self).__init__(pluma.root)

        self.id = id_
        self.notebook = ttk.Notebook(self)

        self.design = DesignEditor(id_, pluma, self, tabs, file_name)
        self.notebook.add(self.design, text='Designer')

        self.xml = XmlEditor(id_, pluma, self, tabs, file_name)
        self.notebook.add(self.xml, text='Xml')

        self.run = RunView(id_, pluma, self, tabs, file_name)
        self.notebook.add(self.run, text='Run...')

        self.notebook.pack(expand=1, fill="both")


class Pluma(UITabsObserver):
    def __init__(self):
        self.root = Tk()
        self.root.title("Pluma - Nuntiare Report Designer")
        self.root.geometry('500x500')

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

    def handle_closetab(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()
            self.views[tabid].destroy()
            del self.views[tabid]
        tabs.remove(tabid)

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

    def save(self, event=None):
        pass

    def save_as(self, event=None):
        pass

    def undo(self, event=None):
        view = self.current_view
        memento = view.xml.memento
        if memento.is_undo_possible():
            history = memento.get_undo_memento()
            if history.type == 'inserted':
                view.xml.widget.delete(
                    history.mark, history.mark_end, True)
            elif  history.type == 'deleted':
                view.xml.widget.insert(
                    history.mark, history.text, True)

    def redo(self, event=None):
        view = self.current_view
        memento = view.xml.memento
        if memento.is_redo_possible():
            history = memento.get_redo_memento()
            if history.type == 'inserted':
                view.xml.widget.insert(
                    history.mark, history.text, True)
            elif  history.type == 'deleted':
                view.xml.widget.delete(
                    history.mark, history.mark_end, True)

    def _verify_undo_redo(self):
        view = self.current_view
        memento = view.xml.memento
        undo_state = DISABLED
        redo_state = DISABLED
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
