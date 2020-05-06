# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from ...common import TextInfoMixin


class HighlightBlocks():
    def __init__(self):
        self._lines = []
        self._to_remove = []

    def set_line(self, number):
        if number > len(self._lines):
            i = len(self._lines)
            while i < number:
                self._lines.append([])
                i += 1

    def check_lines_number(self, count):
        i = 0
        while i < count:
            self._lines.append([])
            i += 1

    def remove_blocks(self, blocks=None):
        for b in self._to_remove:
            if blocks and b not in blocks:
                continue
            x = b.line_start
            while x <= b.line_end:
                line = self.get_line(x)
                line.remove(b)
                x += 1
        if blocks:
            for b in blocks:
                self._to_remove.remove(b)
        else:
            self._to_remove = []

    def get_line(self, number):
        return self._lines[number - 1]

    def add_blocks(self, blocks):
        lines_afected = []
        for b in blocks:
            line = self.get_line(b.line_start)
            if b not in line:
                line.append(b)
                if b.line_start - 1 not in lines_afected:
                    lines_afected.append(b.line_start - 1)

            if b.line_count() > 1:  # Multiline
                print('  Line count(): ' + str(b.line_count()))
                i = b.line_start + 1
                while i <= b.line_end:
                    self.set_line(i)
                    ln = self.get_line(i)
                    if b not in ln:
                        ln.append(b)
                        if ln not in lines_afected:
                            lines_afected.append(i - 1)
                    i += 1
        # Order
        for line in lines_afected:
            self._lines[line] = self.order_blocks(self._lines[line])

    @staticmethod
    def order_blocks(blks):
        if len(blks) < 2:
            return blks
        # order by index_start_int
        n_blks = []
        z_list = []
        for b in blks:
            line = (b.index_start_int(), b)
            z_list.append(line)
        res = sorted(z_list, key=lambda z: z[0])
        for r in res:
            n_blks.append(r[1])
        return n_blks

    def adjust_block_indexes(self, text_info):
        def adjust(block):
            if block.descriptor.type == 'toeol':
                if block.index_end_int() >= text_info.index_start_int():
                    return True
            else:
                if block.index_end_int() > text_info.index_start_int():
                    return True

        print('**** Adjust indexes')

        line_start = self.get_line(text_info.line_start)
        line_count = text_info.line_count()
        to_remove = []

        for b in line_start:
            if text_info.type == 'inserted':
                if adjust(b):
                    if line_count > 1:
                        if text_info.index_start_int() <= b.index_start_int():
                            b.col_start -= text_info.col_start
                            b.col_start += \
                                text_info.length_last_line_affected()
                            b.adjust_line_start = True
                        if b.line_end > text_info.line_start:
                            pass
                        else:
                            b.col_end -= text_info.col_start
                            b.col_end += text_info.length_last_line_affected()
                    else:
                        if b.index_start_int() >= text_info.index_start_int():
                            b.col_start += \
                                text_info.length_last_line_affected()
                        b.col_end += text_info.length_last_line_affected()

            else:  # Deleted
                if text_info.index_start_int() <= b.index_start_int() and \
                        text_info.index_end_int() >= b.index_end_int():
                    to_remove.append(b)
                    continue

                if b.descriptor.type in {'wholeword', 'regex'}:
                    if text_info.index_end_int() <= b.index_start_int():
                        b.col_start += text_info.length_last_line_affected()
                        b.col_end += text_info.length_last_line_affected()
                    elif (text_info.index_start_int() > b.index_start_int()
                            and text_info.index_end_int() < b.index_end_int()):
                        if line_count == 1:
                            b.col_end += text_info.length_last_line_affected()
                        else:
                            if text_info.line_end == b.line_end:
                                b.col_end += text_info.col_start

                elif b.descriptor.type == 'toclosetoken':
                    if text_info.index_end_int() <= b.index_start_int():
                        if line_count == 1:
                            b.col_start -= len(text_info.text)
                            if b.line_count() == 1:
                                b.col_end -= len(text_info.text)
                        else:
                            b.adjust_line_start = True
                            b.col_start -= len(text_info.text)

                    if text_info.index_start_int() > b.index_start_int() and \
                            text_info.index_end_int() < b.index_end_int():
                        if line_count == 1:
                            b.col_end -= len(text_info.text)
                        else:
                            if text_info.line_end == b.line_end:
                                b.col_end += text_info.col_start

                elif b.descriptor.type == 'toeol':
                    if text_info.index_start_int() > b.index_start_int() and \
                            text_info.index_end_int() <= b.index_end_int():
                        b.col_end -= len(text_info.text)

        if to_remove:
            self.remove_blocks(to_remove)

        if line_count > 1:
            self._adjust_lines(text_info)
            self._resize_lines(text_info)

    def _adjust_lines(self, text_info):
        multiline = []
        start_line = text_info.line_start
        count = text_info.line_count()
        factor = 1
        if text_info.type == 'deleted':
            factor = -1

        i = start_line
        while i <= len(self._lines):
            line = self.get_line(i)
            for b in line:
                if b.line_count() > 1:
                    if b in multiline:  # Already adjusted
                        continue

                    x = i + 1
                    while x <= b.line_end:
                        ln = self.get_line(x)
                        if b in ln:
                            ln.remove(b)
                        x += 1
                    multiline.append(b)

                if b.adjust_line_start or \
                        b.line_start > start_line:
                    b.line_start += factor * (count - 1)
                    b.adjust_line_start = None
                    if text_info.type == 'deleted':
                        self._reasign_blokcs(line, [b])
                if text_info.type == 'deleted' and \
                        text_info.index_start_int() >= b.index_end_int():
                    pass
                else:
                    b.line_end += factor * (count - 1)

            i += 1

    def _resize_lines(self, text_info):
        multiline = []
        start_line = text_info.line_start
        i = start_line
        while True:
            if i > len(self._lines):
                break

            line = self.get_line(i)

            res = []
            for b in line:
                if b.line_count() > 1:
                    if b in multiline:  # Already check
                        continue

                if b.line_start > i:
                    res.append(b)

                if b.line_count() > 1:
                    if b.line_start > i:
                        x = b.line_start + 1
                    else:
                        x = start_line + 1

                    while x <= b.line_end:
                        self.set_line(x)
                        ln = self.get_line(x)
                        ln.append(b)
                        x += 1
                    multiline.append(b)

            self._reasign_blokcs(line, res)

            i += 1

        y = 1
        while y <= len(self._lines):
            y += 1

        if text_info.type == 'deleted':
            i = text_info.line_count()
            while i > 1:
                self._lines.pop()
                i -= 1

        y = 1
        while y <= len(self._lines):
            y += 1

    def _reasign_blokcs(self, line, blocks):
        for b in blocks:
            line.remove(b)
            self.set_line(b.line_start)
            ln = self.get_line(b.line_start)
            ln.append(b)

    def blocks_affected(self, text_info):
        '''Returns the list of blocks that were affected by
        text changed, '[]' if no blocks found.
        '''
        res = []
        chg1, chg2 = text_info.index_start_int(), text_info.index_end_int()

        l1, l2 = text_info.line_start, text_info.line_end

        if text_info.type == 'inserted':
            self.check_lines_number(l2 - l1)

        i = l1
        while i <= l2:
            line = self.get_line(i)
            for b in line:
                if b in res:
                    continue

                f1, f2 = b.index_start_int(), b.index_end_int()

                if b.descriptor.type in {'wholeword', 'regex'}:
                    if text_info.type == 'inserted':
                        if ((chg1 == f1 or chg1 == f2) and
                                not b.descriptor.is_separator(
                                    text_info.text, True)):
                            self._to_remove.append(b)
                            res.append(b)
                        if chg1 > f1 and chg1 < f2:
                            self._to_remove.append(b)
                            res.append(b)

                    else:  # deleted
                        if (chg1 < f1 and chg2 >= f1 or
                                chg1 >= f1 and chg1 <= f2):
                            self._to_remove.append(b)
                            res.append(b)

                elif b.descriptor.type in {'toeol'}:
                    if text_info.type == 'inserted':
                        if chg1 > f1 and chg1 <= f2:
                            res.append(b)

                    else:  # deleted
                        if chg1 > f1 and chg1 <= f2:
                            res.append(b)

                elif b.descriptor.type in {'toclosetoken'}:
                    if text_info.type == 'inserted':
                        if chg1 > f1 and chg1 < f2:
                            res.append(b)

                    else:  # deleted
                        if chg1 > f1 and chg1 < f2:
                            res.append(b)

            i += 1

        return res

    def get_available_space(self, text_info):
        '''Returns list with available range info where
        text changed is located.
        [line_start, col_start, line_end, col_end]
        '''
        available = [None, None, None, None]
        line = self.get_line(text_info.line_start)

        for b in line:
            if b.col_end <= text_info.col_start:
                available[0] = b.line_end
                available[1] = b.col_end
            else:
                break
        if available[0] is None:
            available[0] = text_info.line_start
            available[1] = 0

        if text_info.type == 'deleted' and \
                text_info.line_count() > 1:
            line = self.get_line(
                text_info.line_end - text_info.line_count() - 1)
        else:
            line = self.get_line(text_info.line_end)

        for b in line:
            if b.col_start >= text_info.col_end:
                available[2] = b.line_start
                available[3] = b.col_start
                break
        if available[2] is None:
            if text_info.type == 'deleted' and \
                    text_info.line_count() > 1:
                available[2] = text_info.line_end - text_info.line_count() - 1
            else:
                available[2] = text_info.line_end
            available[3] = 10000  # Ensure to EOL

        return available


class HighlightBlock(TextInfoMixin):
    def __init__(self, start_index, end_index, descriptor, state=1):
        super(HighlightBlock, self).__init__()

        self.descriptor = descriptor
        # state -> 0: OPEN, 1: COMPLETED
        self.state = state
        self.line_start, self.col_start = \
            self._get_line_col(start_index)
        self.line_end, self.col_end = \
            self._get_line_col(end_index)
        # Sub blocks
        self.sub_blocks = []
        # Flags for line adjustment
        self.adjust_line_start = None

    def set_index_end(self, index):
        self.line_end, self.col_end = \
            self._get_line_col(index)

    def in_range(self, text_info):
        if self.descriptor.type not in {'toclosetoken', 'toeol'}:
            return

        s = text_info.index_start_int()
        e = text_info.index_end_int()
        ms = self.index_start_int()
        me = self.index_end_int()

        if s >= (ms + len(self.descriptor._tokens[0].value)):
            if self.descriptor.type == 'toclosetoken':
                if e <= (me - len(self.descriptor._tokens[0].close_token)):
                    return True
            else:
                return True

    def block_intersect(self, block):
        '''Blocks in same line'''
        if block.col_end <= self.col_start:
            return
        if block.col_start >= self.col_end:
            return
        if block.col_start > self.col_start and \
                block.col_end > self.col_end:
            return True
        if block.col_start >= self.col_start and \
                block.col_end <= self.col_end:
            return True

    def __str__(self):
        res = '<Block {0} {1}-{2}>'.format(
                self.descriptor.style,
                self.index_start_int(),
                self.index_end_int()
            )
        return res
