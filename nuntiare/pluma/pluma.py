# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import os
from materialtheme import TkMaterialTheme, Theme, ImageManager
from materialtheme.widgets import GroupToolBarTheme as GroupToolBar
from materialtheme.widgets import UITabsTheme as UITabs
from .menu_manager import MenuManager
from .highlight import Highlight
from .view import NuntiareView

DIR = os.path.dirname(os.path.realpath(__file__))


class Pluma(TkMaterialTheme):
    def __init__(self):
        super(Pluma, self).__init__()
        self.title('Pluma - Nuntiare Report Designer')
        self.geometry('800x500')
        self.protocol('WM_DELETE_WINDOW', self.exit_pluma)
        try:
            self.state('zoomed')
        except:
            self.state('-zoomed') # ubuntu?
        #self.wm_attributes('-toolwindow', True)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.highlight = Highlight()
        self.highlight.load_syntax_files()

        Theme.bind('theme_changed', self._on_theme_changed)
        ImageManager.add_image_path(os.path.join(DIR, 'images'))

        self.toolbar = GroupToolBar(self, 48)
        self.toolbar.add_toolbar('file')
        self.toolbar.add_toolbar_item(
                'file', 'new', self.new_file, 'note_add-24px')
        self.toolbar.add_toolbar_item(
                'file', 'open', self.open_file, 'folder-24px')
        self.toolbar.add_toolbar_item(
                'file', 'save', self.open_file, 'save_alt-24px')

        self.toolbar.add_toolbar('undo_redo')
        self.toolbar.add_toolbar_item(
                'undo_redo', 'undo', self.undo, 'undo-24px')
        self.toolbar.add_toolbar_item(
                'undo_redo', 'redo', self.redo, 'redo-24px')

        self.toolbar.add_toolbar('right')
        self.toolbar.add_toolbar_item(
                'right', 'toggle', self._toggle_right_pane,
                'menu-black-24dp', side='right')
        btn_menu = self.toolbar.add_toolbar_item(
                'right', 'more', None, 'more_vert-24px', side='right')
        btn_menu.bind('<Button-1>', self._show_main_menu)
        self.toolbar.grid(column=0, row=0, sticky='we')


        # menu

        self._main_menu = MenuManager.new_menu('main', None, parent=self)

        MenuManager.new_menu('file', 'main')
        MenuManager.add_command(
                'file', 'select_all', 'Select All', 'Ctrl+A',
                command=self.select_all, state=tk.NORMAL)

        #MenuManager.add_command(
        #        'file', 'new', 'New', 'Ctrl+N', self.new_file,
        #        image='note_add-24px', state=tk.NORMAL)
        #MenuManager.add_command(
        #        'file', 'open', 'Open', 'Ctrl+O', self.open_file,
        #        image='folder-24px', state=tk.NORMAL)
        #MenuManager.add_command(
        #        'file', 'save', 'Save', 'Ctrl+S', self.save,
        #        image='save_alt-24px')
        #MenuManager.add_separator('file')

        MenuManager.add_cascade('File', 'main', 'file')

        #MenuManager.new_menu('edit', 'main')
        #MenuManager.add_command(
        #    'edit', 'undo', 'Undo', 'Ctrl+Z',
        #    self.undo, image='undo-24px')
        #self.menu.add_command(
        #    'edit', 'redo', 'Redo', 'Ctrl+Y', self.redo, image='redo')
        #self.menu.add_separator('edit')
        #self.menu.add_command(
        #    'edit', 'copy', 'Copy', 'Ctrl+C', self.copy)
        #self.menu.add_command(
        #    'edit', 'paste', 'Paste', 'Ctrl+V', self.paste)
        #self.menu.add_command(
        #    'edit', 'cut', 'Cut', 'Ctrl+X', self.cut)
        #self.menu.add_separator('edit')
        #self.menu.add_command(
        #    'edit', 'select_all', 'Select All', 'Ctrl+A', self.select_all)

        #MenuManager.add_cascade('Edit', 'main', 'edit')

        MenuManager.add_command(
            'main', 'exit', 'Exit', 'Alt+F4', self.exit_pluma,
            image='close-24px', state=tk.NORMAL)

        # link menu and toolbar items

        #self.menu.linK_menu_toolbar_item('save', 
        #    'file', 'save', 'file', 'save')

        #self.menu.linK_menu_toolbar_item('undo', 
        #    'edit', 'undo', 'undo_redo', 'undo')
        #self.menu.linK_menu_toolbar_item('redo', 
        #    'edit', 'redo', 'undo_redo', 'redo')

        # tabs

        self.tab_count = 1
        self.tabs = UITabs(self)
        self.tabs.bind('tab_added', self._tab_added)
        self.tabs.bind('tab_closed', self._tab_closed)
        self.tabs.bind('tab_selected', self._tab_selected)
        self.tabs.bind('tab_deselected', self._tab_deselected)
        self.tabs.grid(column=0, row=1, sticky='ew')

        self.views = {}
        self.current_view = None

        self.progressbar = ttk.Progressbar(self, orient='horizontal')
        self.progressbar.grid(column=0, row=3, sticky='swe')
        self.progressbar.grid_remove()

        self.set_theme('material')
        self.mainloop()

    def _toggle_right_pane(self):
        if self.current_view:
            self.current_view.current_view.toggle_right_pane()

    def _show_main_menu(self, event):
        try:
            self._main_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self._main_menu.grab_release()

    def _on_theme_changed(self, theme):
        pass

    def _tab_added(self, tabs, tabid=None, file_name=None):
        self.progressbar.grid()
        self.progressbar['mode'] = 'indeterminate'
        self.progressbar.start()

        tabs.add(tabid=self.tab_count,
            title='Untitled ' + str(self.tab_count), dirty=True)
        view = NuntiareView(self.tab_count, self, tabs, file_name)
        view.grid(column=0, row=2, sticky='nwes')
        self.views[self.tab_count] = view
        self.current_view = view
        self.tab_count += 1

        view.xml.text.bind('<Control-c>', self.copy)
        view.xml.text.bind('<Control-C>', self.copy)
        view.xml.text.bind('<Control-v>', self.paste)
        view.xml.text.bind('<Control-V>', self.paste)
        view.xml.text.bind('<Control-x>', self.cut)
        view.xml.text.bind('<Control-X>', self.cut)

        self.progressbar.stop()
        self.progressbar.grid_remove()

    def _tab_closed(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()
            self.views[tabid].destroy()
            del self.views[tabid]
        tabs.remove(tabid)

        if len(tabs.tabs) == 0:
            self.current_view = None
            self._verify_undo_redo()

    def _tab_deselected(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()

    def _tab_selected(self, tabs, tabid):
        if tabid in self.views: 
            view = self.views[tabid]
            view.grid(column=0, row=2, sticky='nwes')
            self.current_view = view
            view.update_toolbar()
            self._verify_undo_redo()

    def new_file(self, event=None):
        self._tab_added(self.tabs)

    def open_file(self, event=None):
        input_file_name = tk.filedialog.askopenfilename(
                defaultextension='.txt',
                filetypes=[("All Files", "*.*"), ("Xml Documents", "*.xml")])
        if input_file_name:
            self._tab_added(self.tabs, file_name=input_file_name)

    def copy(self, event=None):
        view = self.current_view
        copypaste = view.copypaste
        if view and \
                view.current_view.type == 'text':
            txt = view.xml.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if txt is not None:
                copypaste.add_copy(txt)
                return txt
        return 'break'

    def paste(self, event=None):
        view = self.current_view
        copypaste = view.copypaste
        if view and \
                view.current_view.type == 'xml':
            txt = copypaste.get_paste()
            if txt is not None:
                view.xml.text.insert(tk.INSERT, txt[0])
        return 'break'

    def cut(self, event=None):
        txt = self.copy()
        if txt is not None:
            self.current_view.xml.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        return 'break'

    def select_all(self, event=None):
        view = self.current_view
        if view and \
                view.current_view.type == 'text':
            view.xml.text.tag_add('sel', '1.0', 'end')

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
                view.xml.text.delete(
                    history.index_start(), history.index_end(), True)
            elif history.type == 'deleted':
                view.xml.text.insert(
                    history.index_start(), history.text, True)

    def redo(self, event=None):
        view = self.current_view
        memento = view.memento
        if memento.is_redo_possible():
            history = memento.get_redo_memento()
            if history.type == 'inserted':
                view.xml.text.insert(
                    history.index_start(), history.text, True)
            elif history.type == 'deleted':
                view.xml.text.delete(
                    history.index_start(), history.index_end(), True)

    def _verify_undo_redo(self):
        view = self.current_view
        undo_state = tk.DISABLED
        redo_state = tk.DISABLED
        if view is not None:
            memento = view.memento
            if memento.is_undo_possible():
                undo_state = tk.NORMAL
            if memento.is_redo_possible():
                redo_state = tk.NORMAL

    def exit_pluma(self, event=None):
        if tkinter.messagebox.askokcancel("Exit Pluma",
                    "Do you want to exit?\n"
                    "Make sure you've saved your current work."):
            self.destroy()

    def run(self):
        self.mainloop()
