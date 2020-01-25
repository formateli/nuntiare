# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.


class HighlightBlocks():
    def __init__(self):
        self._lines = None

    def set_num_lines(self, count):
        self._lines = []
        i = 0
        while i < count:
            self._lines.append([])
            i += 1

    def add_blocks(self, blocks, order=True):
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

        if order:
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

    def get_line(self, number):
        return self._lines[number - 1]

    def blocks_affected(self, text_info):
        '''This function return a list of two values:
            0: list of blocks that were affected by
               text changed, if any '[]' is returned.
            1: If no blocks affected are found, return the available
               range where text changed is located.
               [line_start, col_start, line_end, col_end] 
        '''

        print('**** Blocks Affected')

        res = []
        m1, m2 = HighlightBlock.get_index_int(text_info.line, text_info.column), \
                HighlightBlock.get_index_int(text_info.line_end, text_info.column_end)
        l1, l2 = text_info.line, text_info.line_end
        print(m1)
        print(m2)
        i = l1
        while i <= l2:
            line = self.get_line(i)
            for b in line:
                if b in res:
                    continue

                f1, f2 = b.index_start_int(), b.index_end_int()
                print(f1)
                print(f2)

                if b.descriptor.type in {'wholeword', 'regex'}:
                    if text_info.type == 'inserted':
                        if (m1 == f1 or m1 == f2) and \
                                not b.descriptor.is_separator(text_info.text):
                            print('m1 == f1 or m1 == f2')
                            res.append(b)
                        if m1 > f1 and m1 < f2:
                            print('m1 > f1 and m1 < f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toeol',}:
                    if text_info.type == 'inserted':
                        if m1 > f1 and m1 <= f2:
                            print('m1 > f1 and m1 <= f2')
                            res.append(b)

                    else: # deleted
                        pass

                elif b.descriptor.type in {'toclosetoken',}:
                    if text_info.type == 'inserted':
                        if m1 > f1 and m1 < f2:
                            print('m1 > f1 and m1 < f2')
                            res.append(b)

                    else: # deleted
                        pass

            i += 1

        available = None
        if not res:
            available = [None, None, None, None]
            line = self.get_line(text_info.line)
            for b in line:
                if b.col_end <= text_info.column:
                    available[0] = b.line_end
                    available[1] = b.col_end
                else:
                    break
            if available[0] is None:
                available[0] = text_info.line
                available[1] = 0

            line = self.get_line(text_info.line_end)
            for b in line:
                if b.col_start >= text_info.column_end:
                    available[2] = b.line_start
                    available[3] = b.col_start
                    break
            if available[2] is None:
                available[2] = text_info.line_end
                available[3] = text_info.column_end

        print(res)
        print(available)

        return res, available


class HighlightBlock():
    def __init__(self, start_index, end_index, descriptor, state=1):
        self.descriptor = descriptor
        self.state = state # 0: OPEN, 1: COMPLETED

        self.line_start, self.col_start = \
            self._get_line_col(start_index)
        self.line_end, self.col_end = \
            self._get_line_col(end_index)
        self.sub_blocks = [] # Sub blocks

    def index_start(self):
        return self._get_index(self.line_start, self.col_start)

    def index_end(self):
        return self._get_index(self.line_end, self.col_end)

    def set_index_end(self, index):
        self.line_end, self.col_end = \
            self._get_line_col(index)

    def index_start_int(self):
        return self.get_index_int(
            self.line_start, self.col_start)

    def index_end_int(self):
        return self.get_index_int(
            self.line_end, self.col_end)

    def _get_index(self, line, col):
        return '{0}.{1}'.format(line, col)

    @staticmethod
    def get_index_int(line, col):
        factor = 1000
        return (factor * line) + col

    def _get_line_col(self, index):
        s = index.split('.')
        return int(s[0]), int(s[1])

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
