# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from collections import deque


class MementoCaretaker():
    def __init__(self):
        self._max_lenght = 15
        self._undo_stack = deque()
        self._redo_stack = deque()
        self._break_chars = [' ', '_', '-', '\n', '\r']

    def get_undo_memento(self):
        res = None
        if self.is_undo_possible():
            res = self._undo_stack.pop()
            self._redo_stack.append(res)
        return res

    def get_redo_memento(self):
        res = None
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

    def insert_memento(self, memento):
        if memento is None:
            return

        # We ensure that undo for inserted text is manipulated as a whole word
        if (memento.type == 'inserted' and not self._is_brake_word(memento.text) and			    
                len(memento.text) == 1 and self.is_undo_possible()):								

            m = self._undo_stack[-1]

            if (m.type == 'inserted' and not self._is_brake_word(m.text)):
                # Append char to last memento and change Pos
                m.text += memento.text
                m.column_end += 1
                m.mark_end = m._get_end_mark()
                return

        self._undo_stack.append(memento)
        self._limit_stack()

    def _limit_stack(self):
        if len(self._undo_stack) > self._max_lenght:
            self._undo_stack.popleft()
        self._redo_stack.clear()

    def _is_brake_word(self, s):
        return s in self._break_chars
