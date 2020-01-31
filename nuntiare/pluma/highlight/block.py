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
            l = self._lines[b.line_start - 1]
            l.append(b)
            if l not in lines_afected:
                lines_afected.append(b.line_start - 1)

            if b.line_end > b.line_start: # Multiline
                i = b.line_start
                while i <= b.line_end:
                    l = self._lines[i - 1]
                    l.append(b)
                    if l not in lines_afected:
                        lines_afected.append(i - 1)
                    i += 1
        # Order
        for l in lines_afected:
            self._lines[l] = self.order_blocks(self._lines[l])

    @staticmethod
    def order_blocks(blks):
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
        print('**** Adjust indexes')

        if text_info.type == 'inserted':
            line_start = self.get_line(text_info.line_start)
            line_count = text_info.line_end - text_info.line_start

            print('  line_start: ' + str(text_info.line_start))
            print('  line_count: ' + str(line_count))
            print('  line_object: ' + str(line_start))

            i = 0
            for b in line_start:
                if b.col_end >= text_info.col_start:
                    print('  b.col_start > text_info.column')
                    print('  ' + str(text_info.length_last_line_affected()))
                    print("  Col start before: {0}".format(b.col_start))
                    print("  Col end before: {0}".format(b.col_end))
                    print("  Changed col start: {0}".format(text_info.col_start))
                    print("  Changed col end: {0}".format(text_info.col_end))
                    if line_count > 0:
                        b.col_start -= text_info.col_start
                        b.col_end -= text_info.col_start
                    else:
                        if b.col_start >= text_info.col_start:
                            b.col_start += text_info.length_last_line_affected()
                        b.col_end += text_info.length_last_line_affected()
                    print("  Col start after: {0}".format(b.col_start))
                    print("  Col end after: {0}".format(b.col_end))
                    
                i += 1

            if line_count > 0:
                self._adjust_lines(
                    text_info.line_start, line_count)
                self._resize_lines(text_info.line_start)

    def _adjust_lines(self, start_line, count):
        print('**** _Adjust lines')
        i = start_line
        while i <= len(self._lines):
            line = self.get_line(i)
            for b in line:
                b.line_start += count
                b.line_end += count
            i += 1

    def _resize_lines(self, start_line):
        print('**** _Resize lines')
        i = start_line
        while True:
            if i > len(self._lines):
                break
            line = self.get_line(i)
            res = []
            for b in line:
                if b.line_start != i:
                    res.append(b)
            for r in res:
                line.remove(r)
                self.set_line(r.line_start)
                line = self.get_line(r.line_start)
                line.append(r)

            i += 1

    def blocks_affected(self, text_info):
        '''Returns the list of blocks that were affected by
        text changed, '[]' if no blocks found. 
        '''

        print('**** Blocks Affected')

        res = []
#        m1, m2 = HighlightBlock.get_index_int(text_info.line, text_info.column), \
#                HighlightBlock.get_index_int(text_info.line_end, text_info.column_end)

        m1, m2 = text_info.index_start_int(), text_info.index_end_int() 

        l1, l2 = text_info.line_start, text_info.line_end
        print('  m1: ' + str(m1))
        print('  m2: ' + str(m2))

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
                        if (m1 == f1 or m1 == f2) and \
                                not b.descriptor.is_separator(text_info.text):
                            print('  m1 == f1 or m1 == f2')
                            res.append(b)
                        if m1 > f1 and m1 < f2:
                            print('  m1 > f1 and m1 < f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toeol',}:
                    if text_info.type == 'inserted':
                        if m1 > f1 and m1 <= f2:
                            print('  m1 > f1 and m1 <= f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toclosetoken',}:
                    if text_info.type == 'inserted':
                        if m1 > f1 and m1 < f2:
                            print('  m1 > f1 and m1 < f2')
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

        for b in line:
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
            available[3] = text_info.col_end

        print('  res: ' + str(available))

        return available


class HighlightBlock(TextInfoMixin):
    def __init__(self, start_index, end_index, descriptor, state=1):
        super(HighlightBlock, self).__init__()

        self.descriptor = descriptor
        self.state = state # 0: OPEN, 1: COMPLETED
        self.line_start, self.col_start = \
            self._get_line_col(start_index)
        self.line_end, self.col_end = \
            self._get_line_col(end_index)
        self.sub_blocks = [] # Sub blocks

    def set_index_end(self, index):
        self.line_end, self.col_end = \
            self._get_line_col(index)

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
