# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from ..common import PanedView, MementoCaretaker
from .text_event import TextEvent
from .highlight import Highlight, HighlightBlocks


class TextView(PanedView):

    _title = None
    _highlight = None

    def __init__(self, view):
        super(TextView, self).__init__(view)
        self.type = 'text'
        frame = self.get_frame()

        self.text = TextEvent(
                frame,
                xscrollcommand=frame.xscrollbar.set,
                yscrollcommand=frame.yscrollbar.set)
        self.text.grid(row=0, column=0, sticky='wens')
        self.text.bind("<<TextModified>>", self.onTextModified)
        self.text.bind('<Control-c>', self._copy)
        self.text.bind('<Control-C>', self._copy)
        self.text.bind('<Control-v>', self._paste)
        self.text.bind('<Control-V>', self._paste)
        self.text.bind('<Control-x>', self._cut)
        self.text.bind('<Control-X>', self._cut)

        self._memento = MementoCaretaker()

        frame.xscrollbar.config(command=self.text.xview)
        frame.yscrollbar.config(command=self.text.yview)

        self.left_window.add(frame, weight=1)

        self._hl = None # Highlight
        self._hl_blocks = HighlightBlocks()
        self.new_file()

    def onTextModified(self, event):
        text_info = event.widget.text_changed_info.copy()
        if not self.text.is_undo_redo:
            self._memento.insert_memento(text_info)
        self._hl.apply_hl(
                self.text, text_info, self._hl_blocks,
                self.view.pluma.progressbar)
        self.text.is_undo_redo = None
        self._verify_undo_redo()

    def new_file(self):
        self.text.delete(1.0, tk.END)
        if self.view.full_file_name is None:
            self._hl = TextView._highlight.get_hl_for_extension('xml')
            self.text.insert('1.0', self.new_snipet(), True)
        else:
            self._hl = TextView._highlight.get_hl_for_extension(self.view.extension)
            self.get_file_content()
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

    def selected(self):
        tb = self.view.pluma.toolbar
        tb.show('text', True)
        tb.show('undo_redo', True)
        self._update_toolbar()

    def deselected(self):
        tb = self.view.pluma.toolbar
        tb.show('text', False)

    def close(self):
        pass

    def _update_toolbar(self):
        tb = self.view.pluma.toolbar
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
        tb = self.view.pluma.toolbar
        tb.enable('undo_redo', 'undo', self._memento.is_undo_possible())
        tb.enable('undo_redo', 'redo', self._memento.is_redo_possible())

    def _init_class(self):
        if TextView._title is None:
            TextView._title = 'Text Editor'

            TextView._highlight = Highlight()
            TextView._highlight.load_syntax_files()

            tb = self.view.pluma.toolbar
            tb.add_toolbar('text', after='file')
            tb.add_toolbar_item(
                    'text', 'copy', None, 'file_copy-24px')
            tb.add_toolbar_item(
                    'text', 'paste', None, 'file_paste-24px')
            tb.add_toolbar_item(
                    'text', 'cut', None, 'file_cut-24px')
            tb.show('text', False)
