# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.


class TextInfoMixin:
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
