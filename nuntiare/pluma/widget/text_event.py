# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import Text, NONE, font, TclError, IntVar


class TextInfoMixin():
    def __init__(self):
        self.line_start = None
        self.col_start = None
        self.line_end = None
        self.col_end = None

    def index_start(self):
        return self._get_index(self.line_start, self.col_start)

    def index_end(self):
        return self._get_index(self.line_end, self.col_end)

    def index_start_int(self):
        return self._get_index_int(
            self.line_start, self.col_start)

    def index_end_int(self):
        return self._get_index_int(
            self.line_end, self.col_end)

    def line_count(self):
        return self.line_end - self.line_start + 1

    @staticmethod
    def _get_index(line, col):
        return '{0}.{1}'.format(line, col)

    @staticmethod
    def _get_index_int(line, col):
        factor = 10000
        return (factor * line) + col

    @staticmethod
    def _get_line_col(index):
        s = index.split('.')
        return int(s[0]), int(s[1])


class TextChangedInfo(TextInfoMixin):
    def __init__(self):
        super(TextChangedInfo, self).__init__()
        self.type = None # inserted, deleted
        self.text = None

    def set_info(self, type_, text_changed, index_start, index_end=None):
        self.type = type_		
        self.text = text_changed

        self.line_start, self.col_start = \
            self._get_line_col(index_start)

        self._affected_factor = 1
        if type_ == 'deleted':
           self._affected_factor = -1

        self._set_index_end_info(index_end)

    def length(self):
        return len(self.text)

    def length_affected(self):
        return self.length() * self._affected_factor

    def length_last_line_affected(self):
        if self.line_start == self.line_end:
            return self.length_affected()
        return self.col_end * self._affected_factor

    def copy(self):
        tci = TextChangedInfo()
        tci.type = self.type
        tci.text = self.text
        tci.line_start = self.line_start
        tci.col_start = self.col_start
        tci.line_end = self.line_end
        tci.col_end = self.col_end
        tci._affected_factor = self._affected_factor
        return tci

    def _set_index_end_info(self, index_end):
        if index_end is None:
            self.line_end, self.col_end = \
                self._get_end_line_col()
        else:
            self.line_end, self.col_end = \
                self._get_line_col(index_end)

    def _get_end_line_col(self):
        txts = self.text.split('\n')
        line_count = len(txts)
        if line_count > 1:
            line = self.line_start + (line_count - 1)
            col = len(txts[-1])
        else:
            line = self.line_start
            col = self.col_start + len(self.text)
        return line, col


class TextEvent(Text):
    def __init__(self, parent, xscrollcommand, yscrollcommand, is_test=False):

        text_editor_font = None
        if not is_test:
            text_editor_font = font.Font(
                family='Courier New', size=14)

        super(TextEvent, self).__init__(parent,
                wrap=NONE,
                font=text_editor_font,
                xscrollcommand=xscrollcommand,
                yscrollcommand=yscrollcommand)

        self.text_changed_info = TextChangedInfo()
        self.is_undo_redo = None
        self.tags_setted = False

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def insert(self, mark, text, is_undo_redo=None):
        self.is_undo_redo = is_undo_redo
        super(TextEvent, self).insert(mark, text)

    def delete(self, mark, mark_end, is_undo_redo=None):
        self.is_undo_redo = is_undo_redo
        super(TextEvent, self).delete(mark, mark_end)

    def set_tags(self, styles):
        if self.tags_setted:
            return
        for name, value in styles.items():
            self.tag_configure(name, foreground=value.fore_color)
            self.tags_setted = True

    def new_int_var(self):
        return IntVar()

    def _proxy(self, command, *args):
        if command in ('insert', 'delete', 'replace'):

            print('==================')
            #print(args)

            if command == 'insert':
                mark = self.index(args[0])
                print('{0} {1}'.format(command, mark))
                self.text_changed_info.set_info(
                        type_='inserted',
                        text_changed=args[1], index_start=mark)

            elif command == 'delete':
                mark_1 = self.index(args[0])
                if args[0] == 'insert-1c':
                    mark_2 = self.index('insert')
                else:
                    mark_2 = self.index(args[1])

                print('{0} {1}-{2}'.format(command, mark_1, mark_2))

                text_deleted = self._get_text_deleted(mark_1, mark_2)
                self.text_changed_info.set_info(
                        type_='deleted',
                        text_changed=text_deleted,
                        index_start=mark_1, index_end=mark_2)

            elif command == 'replace':
                raise Exception("Replace <<TextModified>> Not Implemented")

            print('==================')

        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
        except TclError as er:
            result = None
            #print(er)

        if command in ('insert', 'delete', 'replace'):
            self.event_generate("<<TextModified>>")

        return result

    def _get_text_deleted(self, start, end):
        return self.get(start, end)
