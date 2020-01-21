# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import Text, NONE, font, TclError, IntVar


class TextChangedInfo():
    def __init__(self):
        self.type = None # inserted, deleted
        self.text = None
        self.mark = None
        self.line = None
        self.column = None
        self.mark_end = None
        self.line_end = None
        self.column_end = None
        self._affected_factor = None

    def set_info(self, type_, text_changed, mark, mark_end=None):
        self.type = type_		
        self.text = text_changed
        self.mark = mark
        self.mark_end = mark_end
        self._affected_factor = 1
        if type_ == 'deleted':
           self._affected_factor = -1

        self._set_mark_info()

    def copy(self):
        tci = TextChangedInfo()
        tci.type = self.type		
        tci.text = self.text
        tci.mark = self.mark
        tci.line = self.line
        tci.column = self.column
        tci.mark_end = self.mark_end
        tci.line_end = self.line_end
        tci.column_end = self.column_end
        tci._affected_factor = self._affected_factor
        return tci

    def _set_mark_info(self):
        self.line, self.column = self._get_line_col(self.mark)
        if self.mark_end is None:
            self.mark_end = self._get_end_mark()
        self.line_end, self.column_end = self._get_line_col(self.mark_end)

    def _get_line_col(self, mark):
        c = mark.split('.')
        return int(c[0]), int(c[1])

    def _get_end_mark(self):
        txts = self.text.split('\n')
        if len(txts) > 1:
            line = self.line + (len(txts) - 1)
            col = len(txts[-1])
        else:
            line = self.line
            col = self.column + len(self.text)
        return '{0}.{1}'.format(line, col)


class TextEvent(Text):
    def __init__(self, parent, xscrollcommand, yscrollcommand):

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
            print(value.fore_color)
            self.tag_configure(name, foreground=value.fore_color)
            self.tags_setted = True

    def new_int_var(self):
        return IntVar()

    def _proxy(self, command, *args):
        if command in ('insert', 'delete', 'replace'):

            #print('==================')
            #print('*** ' + command + ' ***')
            #print(args)

            if command == 'insert':
                #print(args[0])
                mark = self.index(args[0])
                #print('  ' + command + ' MARK: ' + mark)
                self.text_changed_info.set_info(
                        type_='inserted',
                        text_changed=args[1], mark=mark)

            elif command == 'delete':
                mark_1 = self.index(args[0])
                if args[0] == 'insert-1c':
                    mark_2 = self.index('insert')
                else:
                    mark_2 = self.index(args[1])

                #print(mark_1)
                #print(mark_2)

                text_deleted = self._get_text_deleted(mark_1, mark_2)
                self.text_changed_info.set_info(
                        type_='deleted',
                        text_changed=text_deleted,
                        mark=mark_1, mark_end=mark_2)

            elif command == 'replace':
                raise Exception("Replace <<TextModified>> Not Implemented")

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
