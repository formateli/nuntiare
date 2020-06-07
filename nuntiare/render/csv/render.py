# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from .. render import Render
from ... import LOGGER


class CsvRender(Render):
    def __init__(self):
        super(CsvRender, self).__init__(extension='csv')
        self.lines = []

    def render(self, report, **kws):
        super(CsvRender, self).render(report, **kws)
        self._render_items(
            report.result.body.items.item_list)
        self._write_to_file()

    def _render_items(self, items):
        if not items:
            return

        for it in items:
            if it.type != 'PageTablix':
                continue

            for row in it.grid_body.rows:
                line = []
                for cell in row.cells:
                    if not cell.object or not cell.object.item_list:
                        continue
                    type_ = cell.object.item_list[0].type
                    if type_ not in ['PageText']:
                        continue
                    item = cell.object.item_list[0]
                    if item.data_element_output == 'NoOutput':
                        continue

                    line.append(self._run_textbox(item))
                    if cell.col_span > 1:
                        x = 1
                        while x < cell.col_span:
                            line.append('')
                            x += 1

                self.lines.append(line)

    def _run_textbox(self, item):
        value = str(item.value_formatted) \
                if item.value_formatted is not None else ''
        return value

    def _get_line_to_write(self, line):
        res = ''
        i = 0
        for l in line:
            res += '"' + l + '"'
            i += 1
            if i != len(line):
                res += ','
        return res

    def _write_to_file(self):
        try:
            f = open(self.result_file, 'wb')
            try:
                for line in self.lines:
                    ln = self._get_line_to_write(line) + '\n'
                    f.write(ln.encode('utf-8'))
            finally:
                f.close()
        except IOError as e:
            LOGGER.error(
                "I/O Error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e),
                True, "IOError")
        except Exception as e:
            LOGGER.error(
                "Unexpected error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e),
                True, "IOError")

    def help(self):
        'CsvRender help'
