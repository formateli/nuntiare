# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Pluma memento test"

from nuntiare.pluma.memento import MementoCaretaker, CopyPaste
from nuntiare.pluma.widget import TextEvent
from tkinter import END
import unittest


class MementoTest(unittest.TestCase):
    def test_memento(self):
        self.text = TextEvent(None, None, None, is_test=True)
        self.text.bind("<<TextModified>>", self.onTextModified)

        self.text.delete(1.0, END, True)

        # Test Undo / Redo
        self.memento = MementoCaretaker()
        self._check_memento_state(0, 0, False, False, '')

        self.text.insert('1.0', 'abc')
        self._check_memento_state(1, 0, True, False, 'abc')

        self.text.insert('insert', 'd')  # 'abc' --> 'abcd'
        self._check_memento_state(1, 0, True, False, 'abcd')

        self.text.insert('insert', ' ')  # 'abcd' --> 'abcd '
        self._check_memento_state(1, 0, True, False, 'abcd ')

        self.text.insert('insert', ' ')  # 'abcd ' --> 'abcd  '
        self._check_memento_state(1, 0, True, False, 'abcd  ')

        self.text.insert('insert', 'e')  # new word 'e'
        self._check_memento_state(2, 0, True, False, 'abcd  e')

        self.text.insert('insert', ' ')  # 'e' --> 'e '
        self._check_memento_state(2, 0, True, False, 'abcd  e ')

        self.text.insert('insert', 'fgh')  # 'fgh' --> 'fgh'
        self._check_memento_state(3, 0, True, False, 'abcd  e fgh')

        self._undo('fgh')
        self._check_memento_state(2, 1, True, True, 'abcd  e ')
        self._undo('e ')
        self._check_memento_state(1, 2, True, True, 'abcd  ')
        self._undo('abcd  ')
        self._check_memento_state(0, 3, False, True, '')

        self._redo('abcd  ')
        self._check_memento_state(1, 2, True, True, 'abcd  ')

        # Add to memento and clear redo stak
        self.text.insert('insert', 'a')
        self._check_memento_state(2, 0, True, False, 'abcd  a')

        # Multiline
        self.text.delete(1.0, END, True)
        self.memento.clear()

        self.text.insert('insert', 'abc def')
        self._check_memento_state(1, 0, True, False, 'abc def')
        self.text.insert('insert', '\n')
        self._check_memento_state(2, 0, True, False, 'abc def\n')
        self.text.insert('insert', 'ghi')
        self._check_memento_state(3, 0, True, False, 'abc def\nghi')

        self.text.delete(1.0, END, True)
        self.memento.clear()

        self.text.insert('insert', 'abc def\nghi jkl\nmno')
        self._check_memento_state(1, 0, True, False, 'abc def\nghi jkl\nmno')
        self._undo('abc def\nghi jkl\nmno')
        self._check_memento_state(0, 1, False, True, '')

        # Test Copy / Paste

        copypaste = CopyPaste()
        self.assertEqual(len(copypaste._copy_stack), 0)
        self.assertEqual(copypaste.is_paste_possible(), False)
        copypaste.add_copy('ABC')
        self.assertEqual(len(copypaste._copy_stack), 1)
        self.assertEqual(copypaste.is_paste_possible(), True)

        res = copypaste.get_paste()
        self.assertEqual(res[0], 'ABC')

        # Allow to add a list of objets
        copypaste.append_copy(
                ['ABC', 'DEF', 'JKL']
            )
        self.assertEqual(len(copypaste._copy_stack), 3)
        res = copypaste.get_paste()
        self.assertEqual(res[0], 'ABC')
        self.assertEqual(res[1], 'DEF')
        self.assertEqual(res[2], 'JKL')

    def onTextModified(self, event):
        if not self.text.is_undo_redo:
            self.memento.insert_memento(
                self.text.text_changed_info.copy())
        self.text.is_undo_redo = None

    def _undo(self, check_text):
        history = self.memento.get_undo_memento()
        self.assertEqual(history.text, check_text)
        if history.type == 'inserted':
            self.text.delete(
                history.index_start(), history.index_end(), True)
        elif history.type == 'deleted':
            self.text.insert(
                history.index_start(), history.text, True)

    def _redo(self, check_text):
        history = self.memento.get_redo_memento()
        self.assertEqual(history.text, check_text)
        if history.type == 'inserted':
            self.text.insert(
                history.index_start(), history.text, True)
        elif history.type == 'deleted':
            self.text.delete(
                history.index_start(), history.index_end(), True)

    def _check_memento_state(
                self, len_undo_stack, len_redo_stack,
                undo_possible, redo_possible, text_text):
        self.assertEqual(len(self.memento._undo_stack), len_undo_stack)
        self.assertEqual(len(self.memento._redo_stack), len_redo_stack)
        self.assertEqual(self.memento.is_undo_possible(), undo_possible)
        self.assertEqual(self.memento.is_redo_possible(), redo_possible)
        content = self.text.get(1.0, 'end-1c')
        self.assertEqual(content, text_text)
