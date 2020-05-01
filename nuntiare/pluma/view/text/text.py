# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from ...memento import MementoCaretaker
from ..common import PanedView
from .text_event import TextEvent


class TextView(PanedView):

    _tool_bar = None

    def __init__(self, id_, pluma, view, tabs):
        super(TextView, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'text'
        frame = self.get_frame()
        self.text = TextEvent(
                frame,
                xscrollcommand=frame.xscrollbar.set,
                yscrollcommand=frame.yscrollbar.set)
        self.text.grid(row=0, column=0, sticky='wens')
        self.text.bind("<<TextModified>>", self.onTextModified)

        self._memento = MementoCaretaker()

        frame.xscrollbar.config(command=self.text.xview)
        frame.yscrollbar.config(command=self.text.yview)

        self.left_window.add(frame, weight=1)

        self.hl = None # Highlight
        self.new_file()

    def onTextModified(self, event):
        text_info = event.widget.text_changed_info.copy()
        if not self.text.is_undo_redo:
            self._memento.insert_memento(text_info)
        self.hl.apply_hl(
                self.text, text_info, self.view.hl_blocks,
                self.pluma.progressbar)
        self.text.is_undo_redo = None
        self._verify_undo_redo()
        self.pluma.menu.link_set_state('save', tk.NORMAL)


    def new_file(self):
        self.text.delete(1.0, tk.END)
        if self.view.full_file_name is None:
            self.hl = self.pluma.highlight.get_hl_for_extension('xml')
            self.text.insert('1.0', self.new_snipet(), True)
            state = tk.NORMAL
        else:
            self.hl = self.pluma.highlight.get_hl_for_extension(self.view.extension)
            self.get_file_content()
            self.tabs.set_title(self.id, self.view.file_name)
            self.tabs.set_dirty(self.id, False)
            self.tabs.set_tooltip(self.id, self.view.full_file_name)
            state = tk.DISABLED
        #self.pluma.menu.link_set_state('save', state)
        self._clear_memento()

    def new_snipet(self):
        xml = '''<?xml version="1.0" ?>
<Nuntiare>
</Nuntiare>'''
        return xml

    def get_file_content(self):
        with open(self.view.full_file_name) as file_:
            self.text.insert(1.0, file_.read(), True)
            self.text.mark_set('insert_remember', 'insert')
            self.text.mark_set('insert', 'end')
            self.text.delete('insert-1c', 'insert', True)
            self.text.mark_set('insert', 'insert_remember')

    def update_toolbar(self):
        tb = self.pluma.toolbar
        tb.set_command('undo_redo', 'undo', self._undo)
        tb.set_command('undo_redo', 'redo', self._redo)
        tb.set_command('text', 'copy', self._copy)
        tb.set_command('text', 'paste', self._paste)
        tb.set_command('text', 'cut', self._cut)
        self._verify_undo_redo()

    def _copy(self):
        print('COPY')

    def _paste(self):
        print('PASTE')

    def _cut(self):
        print('CUT')

    def _undo(self):
        if self._memento.is_undo_possible():
            history = self._memento.get_undo_memento()
            if history.type == 'inserted':
                self.text.delete(
                    history.index_start(), history.index_end(), True)
            elif history.type == 'deleted':
                self.text.insert(
                    history.index_start(), history.text, True)

    def _redo(self):
        if self._memento.is_redo_possible():
            history = self._memento.get_redo_memento()
            if history.type == 'inserted':
                self.text.insert(
                    history.index_start(), history.text, True)
            elif history.type == 'deleted':
                self.text.delete(
                    history.index_start(), history.index_end(), True)

    def _clear_memento(self):
        self._memento.clear()
        self._verify_undo_redo()

    def _verify_undo_redo(self):
        tb = self.pluma.toolbar
        tb.enable('undo_redo', 'undo', self._memento.is_undo_possible())
        tb.enable('undo_redo', 'redo', self._memento.is_redo_possible())

    def _set_tool_bar(self):
        if TextView._tool_bar is None:
            tb = self.pluma.toolbar
            tb.add_toolbar('text', after='file')
            tb.add_toolbar_item(
                    'text', 'copy', None, 'file_copy-24px')
            tb.add_toolbar_item(
                    'text', 'paste', None, 'file_paste-24px')
            tb.add_toolbar_item(
                    'text', 'cut', None, 'file_cut-24px')
            tb.show('text', False)
            TextView._tool_bar = 'text'
