# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk 
from tkinter import ttk
import os
from ttkwidgets import AutoHideScrollbar
from .widget import TextEvent
from .memento import MementoCaretaker, CopyPaste
from .highlight import HighlightBlocks


class FrameScrolled(ttk.Frame):
    def __init__(self, parent):
        super(FrameScrolled, self).__init__(parent)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Horizontal (x) Scroll bar
        self.xscrollbar = AutoHideScrollbar(self, orient=tk.HORIZONTAL)
        self.xscrollbar.grid(row=1, column=0, sticky='ew')

        # Vertical (y) Scroll Bar
        self.yscrollbar = AutoHideScrollbar(self, orient=tk.VERTICAL)
        self.yscrollbar.grid(row=0, column=1, sticky='ns')


class PanedView(ttk.PanedWindow):
    def __init__(self, id_, pluma, view, tabs):
        self.id = id_
        self.pluma = pluma
        self.view = view
        self.widget = None
        self.tabs = tabs
        self.type = None

        super(PanedView, self).__init__(view.notebook, orient=tk.HORIZONTAL)
        self.grid(row=0, column=0, sticky='wens')

        self.left_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.add(self.left_window, weight=4)
        self.right_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.add(self.right_window, weight=1)

        self._right_hidden = False

    def toggle_right_pane(self):
        if self._right_hidden:
            self.add(self.right_window, weight=1)
        else:
            self.forget(1)
        self._right_hidden = not self._right_hidden

    def get_frame(self):
        return FrameScrolled(self.view.notebook)


class DesignEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(DesignEditor, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'designer'
        frame = self.get_frame()
        label = ttk.Label(frame, text='NOT IMPLEMENTED')
        label.grid(row=0, column=0, sticky='wens')
        self.left_window.add(frame, weight=1)


class TextEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(TextEditor, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'xml'
        frame = self.get_frame()
        self.widget = TextEvent(frame,
                xscrollcommand=frame.xscrollbar.set,
                yscrollcommand=frame.yscrollbar.set)
        self.widget.grid(row=0, column=0, sticky='wens')

        self.widget.bind("<<TextModified>>", self.onTextModified)

        frame.xscrollbar.config(command=self.widget.xview)
        frame.yscrollbar.config(command=self.widget.yview)

        self.left_window.add(frame, weight=1)

        self.hl = None # Highlight
        self.new_file()

    def onTextModified(self, event):
        text_info = event.widget.text_changed_info.copy()
        if not self.widget.is_undo_redo:
            self.view.memento.insert_memento(text_info)
        self.hl.apply_hl(
            self.widget, text_info, self.view.hl_blocks, self.pluma.progressbar)
        self.widget.is_undo_redo = None
        self._update_undo_redo()
        self.pluma.menu.link_set_state('save', tk.NORMAL)

    def _update_undo_redo(self):
        self._update_undo_redo_item(
            'undo', self.view.memento.is_undo_possible())
        self._update_undo_redo_item(
            'redo', self.view.memento.is_redo_possible())

    def _update_undo_redo_item(self, name, possible):
        if possible:
            state = NORMAL
        else:
            state = tk.DISABLED
        self.pluma.menu.link_set_state(name, state)

    def new_file(self):
        self.widget.delete(1.0, tk.END)
        if self.view.full_file_name is None:
            self.hl = self.pluma.highlight.get_hl_for_extension('xml')
            self.widget.insert('1.0', self.new_snipet(), True)
            state = tk.NORMAL
        else:
            self.hl = self.pluma.highlight.get_hl_for_extension(self.view.extension)
            self.get_file_content()
            self.tabs.set_title(self.id, self.view.file_name)
            self.tabs.set_dirty(self.id, False)
            self.tabs.set_tooltip(self.id, self.view.full_file_name)
            state = tk.DISABLED
        #self.pluma.menu.link_set_state('save', state)
        self.view.clear_memento()

    def new_snipet(self):
        xml = '''<?xml version="1.0" ?>
<Nuntiare>
</Nuntiare>'''
        return xml

    def get_file_content(self):
        with open(self.view.full_file_name) as file_:
            self.widget.insert(1.0, file_.read(), True)
            self.widget.mark_set('insert_remember', 'insert')
            self.widget.mark_set('insert', 'end')
            self.widget.delete('insert-1c', 'insert', True)
            self.widget.mark_set('insert', 'insert_remember')


class RunView(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(RunView, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'run'
        frame = self.get_frame()
        label = ttk.Label(frame, text='NOT IMPLEMENTED')
        label.grid(row=0, column=0, sticky='wens')
        self.left_window.add(frame, weight=1)


class NuntiareView(ttk.Frame):
    def __init__(self, id_, pluma, tabs, full_file_name):
        super(NuntiareView, self).__init__(pluma)

        self.id = id_
        self.pluma = pluma
        self.full_file_name = full_file_name
        if full_file_name is not None:
            self.file_name = os.path.basename(full_file_name)
            self.extension = self.file_name.split('.')
            if len(self.extension) > 1:
                self.extension = self.extension[1]
            else:
                self.extension = None
        else:
            self.file_name = full_file_name
            self.extension = None

        self.memento = MementoCaretaker()
        self.copypaste = CopyPaste()
        self.hl_blocks = HighlightBlocks()
        self.notebook = ttk.Notebook(self)
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.design = DesignEditor(id_, pluma, self, tabs)
        self.notebook.add(self.design, text='Designer')

        self.xml = TextEditor(id_, pluma, self, tabs)
        self.notebook.add(self.xml, text='Text Editor')

        self.run = RunView(id_, pluma, self, tabs)
        self.notebook.add(self.run, text='Run...')

        self.current_paned_view = self.design

        self.notebook.grid(row=0, column=0, sticky='ewns')
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def tab_changed(self, event):
        nb = event.widget
        name = nb.select()
        obj = nb.nametowidget(name)
        self.current_paned_view = obj
        if obj.type == 'xml':
            state_xml = tk.NORMAL
        else:
            state_xml = tk.DISABLED
        self.pluma.menu.set_menu_command_state(
            'edit', 'select_all', state_xml)
        self.pluma.menu.set_menu_command_state(
            'edit', 'copy', state_xml)
        self.pluma.menu.set_menu_command_state(
            'edit', 'paste', state_xml)
        self.pluma.menu.set_menu_command_state(
            'edit', 'cut', state_xml)

    def clear_memento(self):
        self.memento.clear()
        #self.pluma.menu.link_set_state('undo', tk.DISABLED)
        #self.pluma.menu.link_set_state('redo', tk.DISABLED)
