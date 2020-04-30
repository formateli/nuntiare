# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import os
import tkinter as tk 
from tkinter import ttk
from ..memento import MementoCaretaker, CopyPaste
from ..highlight import HighlightBlocks
from .designer import DesignerView
from .text import TextView
from .run import RunView


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

        self.design = DesignerView(id_, pluma, self, tabs)
        self.notebook.add(self.design, text='Designer')

        self.xml = TextView(id_, pluma, self, tabs)
        self.notebook.add(self.xml, text='Text Editor')

        self.run = RunView(id_, pluma, self, tabs)
        self.notebook.add(self.run, text='Run...')

        self.current_paned_view = self.design

        self.notebook.grid(row=0, column=0, sticky='ewns')
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def get_view(self, type_):
        if type_ == 'text':
            return self.xml
        if type_ == 'run':
            return self.run
        if type_ == 'designer':
            return self.design 

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
