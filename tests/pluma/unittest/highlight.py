# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Pluma Highlight test"

from nuntiare.pluma.highlight import Highlight, HighlightBlocks
from nuntiare.pluma.widget import TextEvent, TextInfoMixin
import unittest


class TagRange(TextInfoMixin):
    def __init__(self, start_index, end_index):
        super(TagRange, self).__init__()
        self.line_start, self.col_start = \
            self._get_line_col(start_index)
        self.line_end, self.col_end = \
            self._get_line_col(end_index)

    @staticmethod
    def get_int_from_index(index):
        l, c = TagRange._get_line_col(index)
        return TagRange._get_index_int(l, c)


class HighlightTest(unittest.TestCase):
    def test_highlight(self):
        self.hl_blocks = None
        self.text = self._reset_text_widget()

        highlight = Highlight()
        highlight.set_syntax(self._get_syntax_python())
        highlight.set_syntax(self._get_syntax_xml())

        self.hl = highlight.get_hl_for_extension('py')

        # Document not loaded, so no tags are set.
        # Just one exists: 'sel'
        self.assertEqual(len(self.text.tag_names()), 1)

        ###############################################

        # load document
        self.text.insert('1.0', 'abc from fgh')

        # Document is loaded, so besides 'sel' tag
        # 'reserved', 'comment' and 'quote' are set.
        self.assertEqual(len(self.text.tag_names()), 4)

        self._get_tag_ranges()
        self._tag_in_range('reserved', 'from', '1.4', '1.8')

        # One line 'abc from fgh'
        self.assertEqual(len(self.hl_blocks._lines), 1)

        line = self.hl_blocks.get_line(1)
        # Just one block for 'from' reserved word
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (1, 4, 1, 8))

        # Add letter 'd' to non block area
        # abcd from fgh
        self.text.insert('1.3', 'd')
        # Remain one line
        self.assertEqual(len(self.hl_blocks._lines), 1)
        line = self.hl_blocks.get_line(1)
        # Remain one block
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (1, 5, 1, 9))

        # Break line at position 4
        # abcd
        #  from fgh
        self.text.insert('1.4', '\n')
        # Two lines now
        self.assertEqual(len(self.hl_blocks._lines), 2)
        # Tags
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '2.0')
        self._tag_in_range('reserved', 'from', '2.1', '2.5')
        self._tag_no_in_range('reserved', '2.6', '2.9')

        line = self.hl_blocks.get_line(2)
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (2, 1, 2, 5))

        # Insert two lines text
        # ab
        # def xyz
        # pqrcd
        #  from fgh
        self.text.insert('1.2', '\ndef xyz\npqr')
        # four lines now
        self.assertEqual(len(self.hl_blocks._lines), 4)
        # Tags
        self._get_tag_ranges()
        self._tag_in_range('reserved', 'def', '2.0', '2.3')

        line = self.hl_blocks.get_line(2)
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (2, 0, 2, 3))

        self._tag_in_range('reserved', 'from', '4.1', '4.5')
        line = self.hl_blocks.get_line(4)
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (4, 1, 4, 5))

        # Test reserved
        # insert just before: Nothimg happens because char is a separator
        self.text.insert('4.1', ' ')
        # Tags
        self._get_tag_ranges()
        self._tag_in_range('reserved', 'from', '4.2', '4.6')

        line = self.hl_blocks.get_line(4)
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (4, 2, 4, 6))

        # insert just after: Nothimg happens because char is a separator
        self.text.insert('4.7', ' ')
        # Tags
        self._get_tag_ranges()
        self._tag_in_range('reserved', 'from', '4.2', '4.6')

        line = self.hl_blocks.get_line(4)
        self.assertEqual(len(line), 1)
        ln = line[0]
        self.assertEqual(
            (ln.line_start, ln.col_start, ln.line_end, ln.col_end),
            (4, 2, 4, 6))

        # insert between: clear tag
        self.text.insert('4.3', ' ')
        # Tags
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '4.2', '4.7')

        line = self.hl_blocks.get_line(4)
        # No blocks
        self.assertEqual(len(line), 0)

        ####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc from fgh')

        # Insert new line between reserved
        self.text.insert('1.6', '\n')
        self.assertEqual(len(self.hl_blocks._lines), 2)
        i = 1
        while i <= 2:
            ln = self.hl_blocks.get_line(1)
            self.assertEqual(len(ln), 0)
            i += 1
        # Tags
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '2.6')

        ####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc fromclass fgh')

        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.17')

        # Break so two new 'reserved' words appears in two lines
        self.text.insert('1.8', '\n')
        # Tags
        self._get_tag_ranges()
        self._tag_in_range('reserved', 'from', '1.4', '1.8')
        self._tag_in_range('reserved', 'class', '2.0', '2.5')

        ####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc fromclass fgh\nclass abc def deh')

        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.17')
        self._tag_in_range('reserved', 'class', '2.0', '2.5')
        self._tag_in_range('reserved', 'def', '2.10', '2.13')

        self.text.insert('1.8', '\n')
        self.assertEqual(len(self.hl_blocks._lines), 3)
        # Tags
        self._get_tag_ranges()
        self._tag_in_range('reserved', 'from', '1.4', '1.8')
        self._tag_in_range('reserved', 'class', '2.0', '2.5')
        self._tag_in_range('reserved', 'class', '3.0', '3.5')
        self._tag_in_range('reserved', 'def', '3.10', '3.13')

        #####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc from fgh')
        self.text.delete('1.3', '1.4')
        # 'abcfrom fgh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 0)  # No blocks
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.11')

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc from fgh')
        self.text.delete('1.8', '1.9')
        # 'abc fromfgh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 0)  # No blocks
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.11')

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc from fgh')
        self.text.delete('1.5', '1.6')
        # 'abc fom fgh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 0)  # No blocks
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.11')

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'abc from fgh')
        self.text.delete('1.4', '1.8')
        # 'abc  fgh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 0)  # No blocks
        self._get_tag_ranges()
        self._tag_no_in_range('reserved', '1.0', '1.8')

        #####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', 'from tkinter import ttk\n'
                         'from tkinter.font import Font\n')
        self.assertEqual(len(self.hl_blocks._lines), 3)
        self._get_tag_ranges()
        ln = self.hl_blocks.get_line(1)
        self._tag_in_range('reserved', 'from', '1.0', '1.4')
        self.assertEqual((ln[0].index_start(), ln[0].index_end()),
                         ('1.0', '1.4'))
        self._tag_in_range('reserved', 'import', '1.13', '1.19')
        self.assertEqual((ln[1].index_start(),  ln[1].index_end()),
                         ('1.13', '1.19'))
        ln = self.hl_blocks.get_line(2)
        self._tag_in_range('reserved', 'from', '2.0', '2.4')
        self.assertEqual((ln[0].index_start(),  ln[0].index_end()),
                         ('2.0', '2.4'))
        self._tag_in_range('reserved', 'import', '2.18', '2.24')
        self.assertEqual((ln[1].index_start(),  ln[1].index_end()),
                         ('2.18', '2.24'))

        self.text.delete('2.29', '3.0')
        self.assertEqual(len(self.hl_blocks._lines), 2)
        self._get_tag_ranges()
        ln = self.hl_blocks.get_line(1)
        self._tag_in_range('reserved', 'from', '1.0', '1.4')
        self.assertEqual((ln[0].index_start(),  ln[0].index_end()),
                         ('1.0', '1.4'))
        self._tag_in_range('reserved', 'import', '1.13', '1.19')
        self.assertEqual((ln[1].index_start(),  ln[1].index_end()),
                         ('1.13', '1.19'))
        ln = self.hl_blocks.get_line(2)
        self._tag_in_range('reserved', 'from', '2.0', '2.4')
        self.assertEqual((ln[0].index_start(),  ln[0].index_end()),
                         ('2.0', '2.4'))
        self._tag_in_range('reserved', 'import', '2.18', '2.24')
        self.assertEqual((ln[1].index_start(),  ln[1].index_end()),
                         ('2.18', '2.24'))

        #####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', '"char1" abc "char2" deh')

        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 2)

        self._get_tag_ranges()
        self._tag_in_range('quote', '"char1"', '1.0', '1.7')
        self.assertEqual(
            (line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end),
            (1, 0, 1, 7))
        self._tag_in_range('quote', '"char2"', '1.12', '1.19')
        self.assertEqual(
            (line[1].line_start, line[1].col_start,
                line[1].line_end, line[1].col_end),
            (1, 12, 1, 19))

        # Delete
        self.text.delete('1.13', '1.14')
        # '"char1" abc "har2" deh'

        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 2)
        self._get_tag_ranges()
        self._tag_in_range('quote', '"har2"', '1.12', '1.18')
        self.assertEqual(
            (line[1].line_start, line[1].col_start,
                line[1].line_end, line[1].col_end),
            (1, 12, 1, 18))

        self.text.delete('1.16', '1.17')
        # '"char1" abc "har" deh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 2)
        self._get_tag_ranges()
        self._tag_in_range('quote', '"har"', '1.12', '1.17')
        self.assertEqual(
            (line[1].line_start, line[1].col_start,
                line[1].line_end, line[1].col_end),
            (1, 12, 1, 17))

        self.text.delete('1.14', '1.15')
        # '"char1" abc "ar" deh'
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 2)
        self._get_tag_ranges()
        self._tag_in_range('quote', '"hr"', '1.12', '1.16')
        self.assertEqual(
            (line[1].line_start, line[1].col_start,
                line[1].line_end, line[1].col_end),
            (1, 12, 1, 16))

        ####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0',
                         '''"""\nline 1\nline 2\nline 3\n"""''')

        self.assertEqual(len(self.hl_blocks._lines), 5)
        i = 1
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (1, 0, 5, 3))
            i += 1

        self.text.insert('5.3', 'c')

        self.text.insert('1.0', '\n')
        self.assertEqual(len(self.hl_blocks._lines), 6)
        self.assertEqual(len(self.hl_blocks.get_line(1)), 0)
        i = 2
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (2, 0, 6, 3))
            i += 1

        self.text.insert('3.1', '\n')
        self.assertEqual(len(self.hl_blocks._lines), 7)
        i = 2
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (2, 0, 7, 3))
            i += 1

        self.text.delete('7.3', '7.4')
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nl\nine 1\nline 2\nline 3\n"""', '2.0', '7.3')
        self._tag_no_in_range('quote', '1.0', '1.1000')
        self.assertEqual(len(self.hl_blocks._lines), 7)
        i = 2
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (2, 0, 7, 3))
            i += 1

        self.text.insert('7.0', '\nabc')
        self.assertEqual(len(self.hl_blocks._lines), 8)
        i = 2
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (2, 0, 8, 6))
            i += 1
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nl\nine 1\nline 2\nline 3\n\nabc"""', '2.0', '8.6')

        self.text.delete('3.1', '4.0')
        self.assertEqual(len(self.hl_blocks._lines), 7)
        i = 2
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (2, 0, 7, 6))
            i += 1
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nline 1\nline 2\nline 3\n\nabc"""', '2.0', '7.6')

        self.text.delete('1.0', '2.0')
        self.assertEqual(len(self.hl_blocks._lines), 6)
        i = 1
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (1, 0, 6, 6))
            i += 1
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nline 1\nline 2\nline 3\n\nabc"""', '1.0', '6.6')

        self.text.insert('1.0', '\n\n')
        self.assertEqual(len(self.hl_blocks._lines), 8)
        i = 3
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (3, 0, 8, 6))
            i += 1

        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nline 1\nline 2\nline 3\n\nabc"""', '3.0', '8.6')

        self.text.insert('4.0', '\n\n')
        self.assertEqual(len(self.hl_blocks._lines), 10)
        i = 3
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (3, 0, 10, 6))
            i += 1
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\n\n\nline 1\nline 2\nline 3\n\nabc"""',
            '3.0', '10.6')

        self.text.delete('4.0', '6.0')
        self.assertEqual(len(self.hl_blocks._lines), 8)
        i = 3
        while i <= len(self.hl_blocks._lines):
            ln = self.hl_blocks.get_line(i)
            self.assertEqual(len(ln), 1)
            self.assertEqual(
                (ln[0].line_start, ln[0].col_start,
                    ln[0].line_end, ln[0].col_end),
                (3, 0, 8, 6))
            i += 1
        self._get_tag_ranges()
        self._tag_in_range(
            'quote', '"""\nline 1\nline 2\nline 3\n\nabc"""', '3.0', '8.6')

        #####################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', '# comment')

        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 1)

        self._get_tag_ranges()
        self._tag_in_range('comment', '# comment', '1.0', '1.9')

        self.assertEqual(
            (line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end),
            (1, 0, 1, 9))

        self.text.insert('1.9', ' x')
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 1)

        self.assertEqual(
            (line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end),
            (1, 0, 1, 11))
        self._get_tag_ranges()
        self._tag_in_range('comment', '# comment x', '1.0', '1.11')

        # delete space
        self.text.delete('1.9', '1.10')
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 1)
        self.assertEqual(
            (line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end),
            (1, 0, 1, 10))
        self._get_tag_ranges()
        self._tag_in_range('comment', '# commentx', '1.0', '1.10')

        self.text.delete('1.9', '1.10')
        line = self.hl_blocks.get_line(1)
        self.assertEqual(len(line), 1)
        self.assertEqual(
            (line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end),
            (1, 0, 1, 9))
        self._get_tag_ranges()
        self._tag_in_range('comment', '# comment', '1.0', '1.9')

        ###################################

        self.text = self._reset_text_widget()
        self.text.insert('1.0', self._get_python_sample_2())

        # Document is loaded, so besides 'sel' tag
        # 'reserved', 'comment' and 'quote' are set.
        self.assertEqual(len(self.text.tag_names()), 4)

        self._get_tag_ranges()

        self._tag_in_range('comment', '# one line comment', '1.0', '1.18')
        self._tag_in_range('reserved', 'class', '2.0', '2.5')
        self._tag_in_range('reserved', 'def', '3.4', '3.7')
        self._tag_in_range('quote', '"#str1"', '4.8', '4.15')
        self._tag_in_range('quote', '"#str2"', '4.17', '4.24')
        self._tag_in_range('quote', '"str1"', '5.13', '5.19')
        self._tag_in_range('quote', '"str2"', '5.22', '5.28')

        # Text widget append a new line at the end
        self.assertEqual(len(self.hl_blocks._lines), 13)

        line = self.hl_blocks.get_line(5)
        self.assertEqual(len(line), 2)

        # Text changed

        # Insert one separator char in a no blocks area
        self.text.insert('5.12', ',')

        line = self.hl_blocks.get_line(5)
        self.assertEqual(len(line), 2)

        self.assertEqual(
            (
                line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end
            ),
            (5, 14, 5, 20)
        )

        self._get_tag_ranges()
        self._tag_in_range('comment', '# one line comment', '1.0', '1.18')
        self._tag_in_range('reserved', 'class', '2.0', '2.5')
        self._tag_in_range('reserved', 'def', '3.4', '3.7')
        self._tag_in_range('quote', '"#str1"', '4.8', '4.15')
        self._tag_in_range('quote', '"#str2"', '4.17', '4.24')
        self._tag_in_range('quote', '"str1"', '5.14', '5.20')
        self._tag_in_range('quote', '"str2"', '5.23', '5.29')

        # insert a new line, so all lines below this sums 1
        self.text.insert('3.19', '\n')

        self.assertEqual(len(self.hl_blocks._lines), 14)

        line = self.hl_blocks.get_line(6)
        self.assertEqual(len(line), 2)

        self.assertEqual(
            (
                line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end
            ),
            (6, 14, 6, 20)
        )

    def _tag_in_range(self, tag_name, txt, start, end):
        ranges = self._ranges[tag_name]
        range_ok = None
        for r in ranges:
            if r.index_start() == start and r.index_end() == end:
                range_ok = True
                break

        if not range_ok:
            raise Exception("Tag '{0}' not in range. '{1}'-'{2}'".format(
                tag_name, start, end))

        self.assertEqual(self.text.get(start, end), txt)

    def _tag_no_in_range(self, tag_name, start, end):
        start_int = TagRange.get_int_from_index(start)
        end_int = TagRange.get_int_from_index(end)
        ranges = self._ranges[tag_name]
        for r in ranges:
            idxs = r.index_start_int()
            if idxs >= start_int and idxs <= end_int:
                raise Exception(
                    "Found in range for tag '{0}'. {1} - {2}".format(
                        tag_name, r.index_start(), r.index_end()))

    def _get_tag_ranges(self):
        res = {}
        tags = self.text.tag_names()

        for tag in tags:
            if tag == 'sel':
                continue
            res[tag] = []
            ranges = self.text.tag_ranges(tag)
            i = 0
            while i < len(ranges):
                res[tag].append(
                        TagRange(ranges[i].string, ranges[i + 1].string)
                    )
                i += 2
        self._ranges = res

    def _reset_text_widget(self):
        text = TextEvent(None, None, None, is_test=True)
        text.bind("<<TextModified>>", self.onTextModified)
        self.hl_blocks = HighlightBlocks()
        return text

    def onTextModified(self, event):
        text_info = self.text.text_changed_info.copy()
        self.hl.apply_hl(self.text, text_info, self.hl_blocks)

    def _get_python_sample_2(self):
        return r'''# one line comment
class ThisIsAClass():
    def def_test():
        "#str1", "#str2"
        abcd "str1" + "str2"
    """
        Multiline 1
        Multiline 2
        Multiline 3
    """
    def other_function():
        # other comment
        '''

    def _get_syntax_python(self):
        return r'''<highlightDefinition caseSensitive="1" extensions="py">
    <styles>
        <style name="reserved" foreColor="blue" backColor=""
            bold="0" italic="0" />
        <style name="comment" foreColor="green" backColor=""
            bold="0" italic="0" />
        <style name="quote" foreColor="red" backColor=""
            bold="0" italic="0" />
    </styles>

    <separators>
        <separator value="." />
        <separator value="," />
        <separator value=":" />
        <separator value="-" />
        <separator value="+" />
        <separator value="=" />
        <separator value="(" />
        <separator value=")" />
        <separator value="[" />
        <separator value="]" />
        <separator value="{" />
        <separator value="}" />
        <separator value=";" />
        <separator value="?" />
    </separators>

    <descriptors>

        <descriptor style="reserved" type="WholeWord"
                description="Set of words to be highlighted" >
            <tokens>
                <token value="and"/>
                <token value="as"/>
                <token value="assert"/>
                <token value="break"/>-
                <token value="class"/>
                <token value="continue"/>
                <token value="def"/>
                <token value="del"/>
                <token value="elif"/>
                <token value="else"/>
                <token value="except"/>
                <token value="False"/>
                <token value="finally"/>
                <token value="for"/>
                <token value="from"/>
                <token value="global"/>
                <token value="if"/>
                <token value="import"/>
                <token value="in"/>
                <token value="is"/>
                <token value="lambda"/>
                <token value="None"/>
                <token value="nonlocal"/>
                <token value="not"/>
                <token value="or"/>
                <token value="pass"/>
                <token value="raise"/>
                <token value="return"/>
                <token value="True"/>
                <token value="try"/>
                <token value="while"/>
                <token value="with"/>
                <token value="yield"/>
                <token value="self"/>
                <token value="super"/>
            </tokens>
        </descriptor>

        <descriptor style="quote" type="ToCloseToken" multiLine="1"
                description="Multiline quote">
            <tokens>
                <token value="&quot;&quot;&quot;"
                    closeToken="&quot;&quot;&quot;"/>
            </tokens>
        </descriptor>

        <descriptor style="quote" type="ToCloseToken"
                description="String between quotes">
            <tokens>
                <token value="&quot;" closeToken="&quot;"/>
            </tokens>
        </descriptor>

        <descriptor style="quote" type="ToCloseToken"
                description="String between single quotes">
            <tokens>
                <token value="'" closeToken="'"/>
            </tokens>
        </descriptor>

        <descriptor style="comment" type="ToEOL" description="Comment line">
            <tokens>
                <token value="#"/>
            </tokens>
        </descriptor>

    </descriptors>

</highlightDefinition>
        '''

    def _get_syntax_xml(self):
        return r'''<highlightDefinition caseSensitive="0"
                extensions="xml,build,page,rdl,rdlc,addin,nuntiare">

    <styles>
        <style name="reserved" foreColor="blue"
            backColor="" bold="0" italic="0" />
        <style name="comment" foreColor="green"
            backColor="" bold="0" italic="0" />
        <style name="attr" foreColor="brown"
            backColor="" bold="0" italic="0" />
        <style name="quote" foreColor="red"
            backColor="" bold="0" italic="0" />
    </styles>

    <separators>
    </separators>

    <descriptors>
        <descriptor style="reserved" type="ToCloseToken"
                description="Xml Element">
            <tokens>
                <token value="&lt;" closeToken="&gt;"/>
            </tokens>
            <!-- Sub descriptors -->
            <descriptors>
                <descriptor style="attr" type="Regex"
                        description="Attribute Name">
                    <tokens>
                        <token value="\s(.*)="/>
                    </tokens>
                </descriptor>
                <descriptor style="quote" type="ToCloseToken"
                        description="Attribute value">
                    <tokens>
                        <token value="&quot;" closeToken="&quot;"/>
                    </tokens>
                </descriptor>
            </descriptors>
        </descriptor>

        <descriptor style="comment" type="ToCloseToken"
                multiLine="1" description="Comment block">
            <tokens>
                <token value="&lt;!--" closeToken="--&gt;" />
            </tokens>
        </descriptor>

    </descriptors>

</highlightDefinition>'''
