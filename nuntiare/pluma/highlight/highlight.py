# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import os
from xml.dom import minidom

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.normpath(os.path.join(DIR, 'syntax'))


class Highlight():
    def __init__(self):
        self._defs = []
        self._def_by_name = {}

        files = os.listdir(DIR)
        for f in files:
            f = os.path.join(DIR, f)
            if os.path.isfile(f) and f.endswith('.xml'):
                doc = minidom.parse(f)
                root = doc.getElementsByTagName('highlightDefinition')
                if root:
                    self._add_def(root[0])

    def get_hl_for_extension(self, extension):
        if extension in self._def_by_name:
            return self._def_by_name[extension]

        for df in self._defs:
            if extension in df.extensions:
                self._def_by_name[extension] = df
                return df

    def _add_def(self, xml):
        df = HighlightDefinition(xml)
        self._defs.append(df)


class XmlMixin():
    def is_comment(self, node):
        if node.nodeName in ('#text', '#comment'):
            return True

    def get_attr_value(self, node, name, default, required=False):
        res = default
        if node.hasAttribute(name):
            res = node.getAttribute(name)
        if required and not res:
            raise Exception("'{0}' value is required by Node '{1}'".format(
                    name, node.nodeName))
        return res

    def get_list(self, str_list):
        if not str_list:
            return
        return str_list.split(',')


class HighlightDefinition(XmlMixin):
    def __init__(self, node):
        self._styles = {}
        self._separators = []
        self._descriptors = []

        case_sensitive = bool(self.get_attr_value(
                node, 'caseSensitive', False))
        self.extensions = self.get_list(
                self.get_attr_value(node, 'extensions', None, True)
            )

        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'styles':
                self._get_styles(n)
            if n.nodeName == 'separators':
                self._get_separators(n)
            if n.nodeName == 'descriptors':
                self._get_descriptors(n, case_sensitive)

    def apply_hl(self, text, text_info, blocks_gtw):
        first_time = not text.tags_setted
        if first_time:
            text.set_tags(self._styles)

        if first_time:
            self._apply_hl_first_time(text, blocks_gtw)
        else:
            self._apply_hl_text_changed(text, text_info, blocks_gtw)

    def _apply_hl_first_time(self, text, blocks_gtw):
        lines = text.get('1.0', 'end').splitlines()
        blocks_gtw.set_num_lines(len(lines))
        i = 1
        start_col = 0
        while i <= len(lines):
            line = lines[i - 1]

            start_index = '{0}.{1}'.format(i, start_col)
            end_index = '{0}.{1}'.format(i, len(line[start_col:]))

            blks, descriptor = self._process_line(
                text, start_index, end_index)

            i += 1
            start_col = 0

            if not blks:
                continue

            blocks_gtw.add_blocks(blks)

            if descriptor is None:
                self._apply_tags(text, blks)
                continue

            # Last block of blks is of 
            # descriptor type 'ToCloseToken' and
            # its state is 0 (open) and it is
            # multi line

            # Appy tags less the last block
            self._apply_tags(text, blks, True)

            last_blk = blks[-1]
            last_index = self._find_multiline_last_index(
                    text, last_blk)
            self._apply_tags(text, [last_blk])

            if last_index is None:
                # Close token not found, so tag is applied to EOF
                break

            i = last_blk.line_end
            start_col = last_blk.col_end

    def _apply_hl_text_changed(self, text, text_info, blocks):
        pass

    def _find_multiline_last_index(self, text, block):
        if block.descriptor.type not in {'ToCloseToken',}:
            raise Exception(
                "Descriptor must be type of 'ToCloseToken'")

        count = text.new_int_var()

        index = text.search(block.descriptor._pattern_2,
                    block.index_start(), 'end', count=count, regexp=True)

        state = 0
        if index == '' or count.get() == 0:
            res = None
            block.set_index_end(text.index('end'))
        else:
            res = text.index(
                '{0}+{1}c'.format(index, count.get()))
            block.set_index_end(res)
            block.state = 1 # Completed, because close_token was found.
        return res

    def _apply_tags(self, text, blocks, ommit_last_block=False):
        i = len(blocks)
        if ommit_last_block:
            i -= 1
        if i <= 0:
            return

        i -= 1
        x = 0
        while x <= i: 
            b = blocks[x]
            text.tag_add(
                b.descriptor.style, 
                b.index_start(),
                b.index_end())
            if b.sub_blocks:
                self._apply_tags(text, b.sub_blocks)
            x += 1

    def _process_line(self, text, start_index, end_index):
        blks = []
        for d in self._descriptors:
            blks += d.get_blocks(text, start_index, end_index)

        if not blks:
            return None, None

        blks = self._purge(blks)
        last_blk = blks[-1]

        for b in blks:
            if b.descriptor._descriptors: # Sub descriptors
                for d in b.descriptor._descriptors:
                    b.sub_blocks = d.get_blocks(
                        text, b.index_start(), b.index_end())

        if last_blk.descriptor.type == 'ToCloseToken' and \
                last_blk.state == 0 and \
                last_blk.descriptor.multi_line:
            return blks, last_blk.descriptor

        return blks, None

    def _purge(self, blks):
        if len(blks) in [0, 1]:
            return blks

        print('*** PURGE')

        # order by start col
        n_blks = []

        z_list = []
        for b in blks:
            l = (b.col_start, b)
            z_list.append(l)
        res = sorted(z_list, key=lambda z: z[0])
        for r in res:
            n_blks.append(r[1])

        for b in n_blks:
            print(b.descriptor.style)
            print(' ' + str(b.col_start))

        # Verify if blocks intersects each other and delete
        res = []
        for b in n_blks:
            self._mark_for_delete(b, n_blks, res)

        for r in res:
            print(r)
            n_blks.remove(r)

        for b in n_blks:
            print(b.descriptor.style)

        return n_blks

    def _mark_for_delete(self, block, blks, found):
        for b in blks:
            if b == block:
                continue
            if block.block_intersect(b):
                if b not in found:
                    found.append(b)

    def _get_styles(self, node):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'style':
                style = HighlightStyle(n)
                self._styles[style.name] = style

    def _get_separators(self, node):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'separator':
                self._separators.append(self.get_attr_value(
                        n, 'value', None, True)
                    )

    def _get_descriptors(self, node, case_sensitive):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'descriptor':
                descriptor = HighlightDescriptor(n, case_sensitive)
                self._descriptors.append(descriptor)


class HighlightDescriptor(XmlMixin):
    def __init__(self, node, case_sensitive):
        self.type = self.get_attr_value(
                node, 'type', None, True)
        self.style = self.get_attr_value(
                node, 'style', None, True)
        self.multi_line = bool(self.get_attr_value(
                node, 'multiLine', False))
        self._descriptors = [] # Sub drescriptors. Ex: xml attribute name/value
        self._tokens = []

        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'tokens':
                self._add_tokens(n)
            if n.nodeName == 'descriptors':
                self._get_descriptors(n, case_sensitive)

        self._pattern, self._pattern_1, self._pattern_2 = \
                    self._get_pattern()

    def get_blocks(self, text, start, end):
        if not self._pattern:
            return

        blocks = []
        text.mark_set('startIndex', start)
        count = text.new_int_var()

        while True:
            index = text.search(self._pattern, 'startIndex', end,
                                count=count, regexp=True)
            if index == '' or count.get() == 0:
                if self.type in {'WholeWord', 'ToEOL'}:
                    break
                else:
                    res_multiline = self._to_close_token_open_search(
                            text, 'startIndex', end, count)
                    if not res_multiline:
                        break
                    blocks.append(HighlightBlock(
                            res_multiline[0],
                            res_multiline[1],
                            descriptor=self,
                            state=0 # open
                        )
                    )
                    text.mark_set('startIndex', res_multiline[1])
            else:
                end_index = text.index('{0}+{1}c'.format(index, count.get()))
                blocks.append(HighlightBlock(
                        index, 
                        end_index,
                        descriptor=self)
                    )
                text.mark_set('startIndex', end_index)

        return blocks

    def _to_close_token_open_search(self, text, start, end, count):
        '''
        This function finds a match of the 'ToCloseToken' descriptor that
        its close_token is not present in range, so its end match is the
        end of range.
        Return a tuple
        [startIndex, endIndex]
        '''

        if self.type not in {'ToCloseToken',}:
            return

        index = text.search(self._pattern_1,
                    start, end, count=count, regexp=True)

        if index == '' or count.get() == 0:
            return

        return [
                index,
                text.index('{0}+{1}c'.format(index, count.get())),
            ]

    def _add_tokens(self, node):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'token':
                token = HighlightToken(n)
                self._tokens.append(token)

    def _get_pattern(self):
        pattern = ''
        pattern_1 = None # For
        pattern_2 = None # Multiline search
        
        if self.type == 'WholeWord':
            for token in self._tokens:
                if pattern != '':
                    pattern += '|'
                pattern += token.value
            if pattern != '':
                pattern = r'\y(' + pattern + r')\y'

        elif self.type == 'ToEOL':
            pattern = self._tokens[0].value
            pattern += r'.*'

        elif self.type == 'ToCloseToken':
            pattern = self._tokens[0].value
            pattern += r'(.*?)'
            #pattern += r'(.*)'
            pattern += self._tokens[0].close_token
            pattern_1 = self._tokens[0].value + r'.*'
            pattern_2 = r'(.*?)' + self._tokens[0].close_token

        return pattern, pattern_1, pattern_2

    def _get_descriptors(self, node, case_sensitive):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'descriptor':
                descriptor = HighlightDescriptor(n, case_sensitive)
                self._descriptors.append(descriptor)


class HighlightStyle(XmlMixin):
    def __init__(self, node):
        self.name = self.get_attr_value(
                node, 'name', None, True)
        self.fore_color = self.get_attr_value(
                node, 'foreColor', None)
        self.back_color = self.get_attr_value(
                node, 'backColor', None) 
        self.bold = bool(self.get_attr_value(
                node, 'bold', False))
        self.italic = bool(self.get_attr_value(
                node, 'italic', False))


class HighlightToken(XmlMixin):
    def __init__(self, node):
        self.value = self.get_attr_value(
                node, 'value', None, True)
        self.close_token = self.get_attr_value(
                node, 'closeToken', None)
        self.escape_token = self.get_attr_value(
                node, 'escapeToken', None)


class HighlightBlocks():
    def __init__(self):
        self._lines = None

    def set_num_lines(self, count):
        self._lines = []
        i = 0
        while i < count:
            self._lines.append([])
            i += 1

    def add_blocks(self, blocks):
        for b in blocks:
            l = self._lines[b.line_start - 1]
            l.append(b)
            if b.line_end > b.line_start: # Multiline
                i = b.line_start
                while i <= b.line_end:
                    l = self._lines[i - 1]
                    l.append(b)
                    i += 1


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

    def _get_index(self, line, col):
        return '{0}.{1}'.format(line, col)

    def _get_line_col(self, index):
        s = index.split('.')
        return int(s[0]), int(s[1])

    def block_intersect(self, block):
        if block.line_start < self.line_start:
            return
        if block.line_start > self.line_end:
            return
        if block.line_end == self.line_start and \
                block.col_start >= self.col_end:
            return
        if block.line_start == self.line_start and \
                block.col_start < self.col_start and \
                block.col_end <= self.col_start:
            return
        if block.line_start == self.line_start and \
                block.col_start <= self.col_start and \
                block.descriptor.type != 'WholeWord':
            return
        return True
