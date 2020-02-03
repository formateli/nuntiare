# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from ..widget import TextInfoMixin


class HighlightBlocks():
    def __init__(self):
        self._lines = []

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

    def remove_lines(self, line_start, line_end):
        pass

    def get_line(self, number):
        return self._lines[number - 1]

    def remove_blocks(self, blocks):
        for b in blocks:
            x = b.line_start
            while x <= b.line_end:
                l = self.get_line(x)
                l.remove(b)
                x += 1

    def add_blocks(self, blocks):
        lines_afected = []
        for b in blocks:
            line = self.get_line(b.line_start)
            if not b in line:
                line.append(b)
                if b.line_start - 1 not in lines_afected:
                    lines_afected.append(b.line_start - 1)

            if b.line_count() > 1: # Multiline
                print('  Line count(): ' + str(b.line_count()))
                i = b.line_start + 1
                while i <= b.line_end:
                    self.set_line(i)
                    l = self.get_line(i)
                    if b not in l:
                        l.append(b)
                        if l not in lines_afected:
                            lines_afected.append(i - 1)
                    i += 1
        # Order
        for l in lines_afected:
            self._lines[l] = self.order_blocks(self._lines[l])

    @staticmethod
    def order_blocks(blks):
        if len(blks) < 2:
            return blks
        # order by index_start_int
        n_blks = []
        z_list = []
        for b in blks:
            l = (b.index_start_int(), b)
            z_list.append(l)
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

        print('  line_start: ' + str(text_info.line_start))
        print('  line_count: ' + str(line_count))
        print('  line_object: ' + str(line_start))

        if text_info.type == 'inserted':
            for b in line_start:
                print("  b.index_start_int(): {0}".format(b.index_start_int()))
                print("  b.index_end_int(): {0}".format(b.index_end_int()))
                print("  tchg.index_start_int(): {0}".format(text_info.index_start_int()))
                print("  tchg.index_end_int(): {0}".format(text_info.index_end_int()))

                if adjust(b):
                    print('  -- b.index_end_int() > text_info.index_start_int() --')
                    if line_count > 1:
                        b.adjust_line_start = False
                        if text_info.index_start_int() <= b.index_start_int():
                            b.col_start -= text_info.col_start
                            b.col_start += text_info.length_last_line_affected()
                            b.adjust_line_start = True
                        if b.line_end  > text_info.line_start:
                            pass
                        else:
                            b.col_end -= text_info.col_start
                            b.col_end += text_info.length_last_line_affected()
                    else:
                        if b.index_start_int() >= text_info.index_start_int():
                            b.col_start += text_info.length_last_line_affected()
                        b.col_end += text_info.length_last_line_affected()
                    print("  After b.index_start_int(): {0}".format(b.index_start_int()))
                    print("  After b.index_end_int(): {0}".format(b.index_end_int()))

            if line_count > 1:
                self._adjust_lines(
                    text_info.line_start, line_count)
                self._resize_lines(text_info.line_start)

        if text_info.type == 'deleted':
            pass


    def _adjust_lines(self, start_line, count):
        print('**** _Adjust lines')
        i = start_line
        multiline = []
        print('  Total lines: ' + str(len(self._lines)))
        while i <= len(self._lines):
            line = self.get_line(i)
            print('  Line: {0}'.format(i))
            for b in line:
                if b.line_count() > 1:
                    print('  Multiline')
                    if b in multiline: # Already adjusted
                        print('   Already adjusted')
                        continue

                    print('   Verifying multiline')
                    x = b.line_start + 1
                    while x <= b.line_end:
                        l = self.get_line(x)
                        if b in l:
                            print('   Removing b from line: ' + str(x))
                            l.remove(b)
                        x += 1
                    multiline.append(b)

                print('  cur line start: {0}'.format(b.line_start))
                print('  cur line end: {0}'.format(b.line_end))

                if b.line_start < start_line:
                    print('  Adding again b to line: ' + str(start_line))
                    l = self.get_line(start_line)
                    l.append(b)
                if b.adjust_line_start:
                    b.line_start += (count - 1)
                b.adjust_line_start = True
                b.line_end += (count - 1)

                print('  new line start: {0}'.format(b.line_start))
                print('  new line end: {0}'.format(b.line_end))

            i += 1

    def _resize_lines(self, start_line):
        print('**** _Resize lines')
        multiline = []
        line_to_order = []
        i = start_line
        while True:
            print('  Line: ' + str(i))
            if i > len(self._lines):
                break
            line = self.get_line(i)
            print(line)
            res = []
            for b in line:
                if b.line_count() > 1:
                    if b in multiline: # Already check
                        continue

                if b.line_start > i:
                    print('  {0} != {1}'.format(b.line_start, i))
                    res.append(b)

                if b.line_count() > 1:
                    if b.line_start > i:
                        x = b.line_start + 1
                    else:
                        x = start_line + 1
                    while x <= b.line_end:
                        print('  Multiline: ' + str(x))
                        self.set_line(x)
                        l = self.get_line(x)
                        l.append(b)
                        x += 1
                    multiline.append(b)

            for r in res:
                line.remove(r)
                self.set_line(r.line_start)
                l = self.get_line(r.line_start)
                l.append(r)

            i += 1

    def blocks_affected(self, text_info):
        '''Returns the list of blocks that were affected by
        text changed, '[]' if no blocks found. 
        '''

        print('**** Blocks Affected')

        res = []
        chg1, chg2 = text_info.index_start_int(), text_info.index_end_int() 

        l1, l2 = text_info.line_start, text_info.line_end
        print('  chg1: ' + str(chg1))
        print('  chg2: ' + str(chg2))

        if text_info.type == 'inserted':
            self.check_lines_number(l2 - l1)

        i = l1
        while i <= l2:
            line = self.get_line(i)
            for b in line:
                if b in res:
                    continue

                f1, f2 = b.index_start_int(), b.index_end_int()
                print('  f1: ' + str(f1))
                print('  f2: ' + str(f2))

                if b.descriptor.type in {'wholeword', 'regex'}:
                    if text_info.type == 'inserted':
                        if (chg1 == f1 or chg1 == f2) and \
                                not b.descriptor.is_separator(text_info.text):
                            print('  chg1 == f1 or chg1 == f2')
                            res.append(b)
                        if chg1 > f1 and chg1 < f2:
                            print('  chg1 > f1 and chg1 < f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toeol',}:
                    if text_info.type == 'inserted':
                        if chg1 > f1 and chg1 <= f2:
                            print('  chg1 > f1 and chg1 <= f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toclosetoken',}:
                    if text_info.type == 'inserted':
                        if chg1 > f1 and chg1 < f2:
                            print('  chg1 > f1 and chg1 < f2')
                            res.append(b)

                    else: # deleted
                        pass

            i += 1

        print('  res: ' + str(res))

        return res

    def get_available_space(self, text_info):
        '''Returns list with available range info where text changed is located.
        [line_start, col_start, line_end, col_end] 
        '''

        print('**** Available Space')

        available = [None, None, None, None]
        line = self.get_line(text_info.line_start)
        print('  len line: {0}'.format(len(line)))

        for b in line:
            print('  Txt changed col start: {0}'.format(text_info.col_start))
            print('  Line end: {0}'.format(b.line_end))
            print('  Col end: {0}'.format(b.col_end))
            print('  Index start: {0}'.format(b.index_start()))
            print('  Index end: {0}'.format(b.index_end()))
            if b.col_end <= text_info.col_start:
                available[0] = b.line_end
                available[1] = b.col_end
            else:
                break
        if available[0] is None:
            available[0] = text_info.line_start
            available[1] = 0

        line = self.get_line(text_info.line_end)
        for b in line:
            if b.col_start >= text_info.col_end:
                available[2] = b.line_start
                available[3] = b.col_start
                break
        if available[2] is None:
            available[2] = text_info.line_end
            available[3] = 10000 # Ensure to EOL

        print('  res: ' + str(available))

        return available


class HighlightBlock(TextInfoMixin):
    def __init__(self, start_index, end_index, descriptor, state=1):
        super(HighlightBlock, self).__init__()

        self.descriptor = descriptor
        # 0: OPEN, 1: COMPLETED
        self.state = state
        self.line_start, self.col_start = \
            self._get_line_col(start_index)
        self.line_end, self.col_end = \
            self._get_line_col(end_index)
        # Sub blocks
        self.sub_blocks = []
        # Flags for line adjustment
        self.adjust_line_start = True

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
