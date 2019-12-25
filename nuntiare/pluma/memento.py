# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from collections import deque


class MementoCaretaker():
    def __init__(self):
        self._max_lenght = 15
        self._undo_stack = deque()
        self._redo_stack = deque()
        self._break_chars = [' ', '\n']
        self._last_char = None

    def get_undo_memento(self):
        res = None
        self._last_char = self._break_chars[0]
        if self.is_undo_possible():
            res = self._undo_stack.pop()
            self._redo_stack.append(res)
        return res

    def get_redo_memento(self):
        res = None
        self._last_char = self._break_chars[0]
        if self.is_redo_possible():
            res = self._redo_stack.pop()
            self._undo_stack.append(res)
        return res

    def is_undo_possible(self):
        return len(self._undo_stack) > 0

    def is_redo_possible(self):
        return (len(self._redo_stack) > 0)

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def insert_memento(self, text_info):
        if text_info is None or len(text_info.text) == 0:
            return

        if text_info.type == 'inserted':
            end_char = None
            c = text_info.text[-1]
            if c in self._break_chars:
                end_char = c

            if text_info.text == '\n' or self._last_char == '\n':
                self._undo_stack.append(text_info)
            elif self.is_undo_possible() and (self._last_char is None or
                    (self._last_char is not None and end_char is not None and
                        len(text_info.text) == 1)):
                # Append text to last text and change Pos
                m = self._undo_stack[-1]
                m.text += text_info.text
                m.column_end += len(text_info.text)
                m.mark_end = m._get_end_mark()
            else:
                self._undo_stack.append(text_info)

            self._last_char = end_char

        self._limit_stack()

    def _limit_stack(self):
        if len(self._undo_stack) > self._max_lenght:
            self._undo_stack.popleft()
        self._redo_stack.clear()

    def _is_brake_word(self, s):
        return s in self._break_chars
