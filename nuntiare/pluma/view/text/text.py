# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from ..common import PanedView
from .text_event import TextEvent


class TextView(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(TextView, self).__init__(
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
