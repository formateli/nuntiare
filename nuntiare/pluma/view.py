# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import *
from tkinter import ttk
import os
from .widget import TextEvent
from .memento import MementoCaretaker, CopyPaste
from .highlight import HighlightBlocks


class PanedView(ttk.PanedWindow):
    def __init__(self, id_, pluma, view, tabs):
        self.id = id_
        self.pluma = pluma
        self.view = view
        self.widget = None
        self.tabs = tabs
        self.type = None

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


class DesignEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(DesignEditor, self).__init__(
            id_, pluma, view, tabs)

        self.type = 'designer'
        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class TextEditor(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(TextEditor, self).__init__(
            id_, pluma, view, tabs)

        self.type = 'xml'
        self.widget = TextEvent(self.left_frame,
                xscrollcommand=self.xscrollbar.set,
                yscrollcommand=self.yscrollbar.set)
        self.widget.pack(fill=BOTH, expand=1)

        self.widget.bind("<<TextModified>>", self.onTextModified)

        self.xscrollbar.config(command=self.widget.xview)
        self.yscrollbar.config(command=self.widget.yview)

        self.hl = None # Highlight
        self.new_file()

    def onTextModified(self, event):
        text_info = event.widget.text_changed_info.copy()
        if not self.widget.is_undo_redo:
            self.view.memento.insert_memento(text_info)
        self.hl.apply_hl(self.widget, text_info, self.view.hl_blocks)
        self.widget.is_undo_redo = None
        self._update_undo_redo()
        self.pluma.menu.link_set_state('save', NORMAL)

    def _update_undo_redo(self):
        self._update_undo_redo_item(
            'undo', self.view.memento.is_undo_possible())
        self._update_undo_redo_item(
            'redo', self.view.memento.is_redo_possible())

    def _update_undo_redo_item(self, name, possible):
        if possible:
            state = NORMAL
        else:
            state = DISABLED
        self.pluma.menu.link_set_state(name, state)

    def new_file(self):
        self.widget.delete(1.0, END)
        if self.view.full_file_name is None:
            self.hl = self.pluma.highlight.get_hl_for_extension('xml')
            self.widget.insert('1.0', self.new_snipet(), True)
            state = NORMAL
        else:
            self.hl = self.pluma.highlight.get_hl_for_extension(self.view.extension)
            self.get_file_content()
            self.tabs.set_title(self.id, self.view.file_name)
            self.tabs.set_dirty(self.id, False)
            self.tabs.set_tooltip(self.id, self.view.full_file_name)
            state = DISABLED
        self.pluma.menu.link_set_state('save', state)
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
        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class NuntiareView(ttk.Frame):
    def __init__(self, id_, pluma, tabs, full_file_name):
        super(NuntiareView, self).__init__(pluma.root)

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

        self.design = DesignEditor(id_, pluma, self, tabs)
        self.notebook.add(self.design, text='Designer')

        self.xml = TextEditor(id_, pluma, self, tabs)
        self.notebook.add(self.xml, text='Text Editor')

        self.run = RunView(id_, pluma, self, tabs)
        self.notebook.add(self.run, text='Run...')

        self.current_paned_view = self.design

        self.notebook.pack(expand=1, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def tab_changed(self, event):
        nb = event.widget
        name = nb.select()
        obj = nb.nametowidget(name)
        self.current_paned_view = obj
        if obj.type == 'xml':
            state_xml = NORMAL
        else:
            state_xml = DISABLED
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
        self.pluma.menu.link_set_state('undo', DISABLED)
        self.pluma.menu.link_set_state('redo', DISABLED)
