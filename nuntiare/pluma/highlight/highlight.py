# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import os
from xml.dom import minidom
from .block import HighlightBlocks, HighlightBlock


class Highlight():
    def __init__(self):
        self._defs = []
        self._def_by_name = {}

    def load_syntax_files(self):
        dir_ = os.path.dirname(os.path.realpath(__file__))
        dir_ = os.path.normpath(os.path.join(dir_, 'syntax'))
        files = os.listdir(dir_)
        for f in files:
            f = os.path.join(dir_, f)
            if os.path.isfile(f) and f.endswith('.xml'):
                doc = minidom.parse(f)
                self._add_def(doc)

    def set_syntax(self, str_syntax):
        doc = minidom.parseString(str_syntax)
        self._add_def(doc)

    def get_hl_for_extension(self, extension):
        if extension in self._def_by_name:
            return self._def_by_name[extension]

        for df in self._defs:
            if extension in df.extensions:
                self._def_by_name[extension] = df
                return df

    def _add_def(self, doc):
        root = doc.getElementsByTagName('highlightDefinition')
        if not root:
            return
        df = HighlightDefinition(root[0])
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
        self._apply_hl(text, blocks_gtw, 1, 0, 'end')

    def _apply_hl_text_changed(self, text, text_info, blocks_gtw):
        blks_affected = blocks_gtw.blocks_affected(text_info)
        print(blks_affected)

        if not blks_affected:
            blocks_gtw.adjust_block_indexes(text_info)
            avbl_range = blocks_gtw.get_available_space(text_info)

            if text_info.type == 'inserted':
                if self._is_separator(text_info.text):
                    return
                else:
                    print(avbl_range)
                    self._apply_hl(
                        text, blocks_gtw,
                        avbl_range[0], avbl_range[1],
                        '{0}.{1}'.format(avbl_range[2], avbl_range[3]))

            else: # deleted
                self._apply_hl(
                    text, blocks_gtw,
                    avbl_range[0], avbl_range[1],
                    '{0}.{1}'.format(avbl_range[2], avbl_range[3]))

        if len(blks_affected) == 1:
            b = blks_affected[0]
            if b.descriptor.type in {'wholeword', 'regex'}:
                # Alway affected
                # remove tag
                # remove block
                # reblocks and retags the new available area
                # adjust_block_indexes
                pass
            if b.descriptor.type in {'toeol', 'toclosetoken'}:
                return

    def _apply_hl(self, text, blocks_gtw,
                line_start, col_start, index_end):
        print('APLY HL() ***')

        lines = text.get(
            '{0}.{1}'.format(line_start, col_start),
            index_end).splitlines()

        cur_line = line_start
        line_count = 0
        end_line = line_start + (len(lines) - 1)
        start_col = col_start
        first_iter = True

        while cur_line <= end_line:
            line = lines[line_count]
            blocks_gtw.set_line(cur_line)

            print('  ' + line)
            start_index = '{0}.{1}'.format(cur_line, start_col)
            if first_iter:
                end_index = '{0}.{1}'.format(cur_line, start_col + len(line))
            else:
                end_index = '{0}.{1}'.format(cur_line, len(line[start_col:]))
            first_iter = False

            print('  ' + start_index)
            print('  ' + end_index)

            blks, descriptor = self._process_line(
                text, start_index, end_index)

            cur_line += 1
            start_col = 0
            line_count += 1

            print('  blks: ' + str(blks))
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
            #print('LAST INDEX: ' + last_index)
            #print('LAST INDEX: ' + last_blk.index_end())
            self._apply_tags(text, [last_blk])

            if last_index is None:
                # Close token not found, so tag is applied to EOF
                break

            cur_line = last_blk.line_end
            start_col = last_blk.col_end
            line_count = last_blk.line_end - line_start

    def _is_separator(self, txt):
        if len(txt) != 1:
            return
        return txt == ' ' or txt in self._separators

    def _find_multiline_last_index(self, text, block):
        if block.descriptor.type not in {'toclosetoken',}:
            raise Exception(
                "Descriptor must be type of 'ToCloseToken'")

        count = text.new_int_var()

        start = '{0}+{1}c'.format(
            block.index_start(), len(block.descriptor._tokens[0].value))

        index = text.search(block.descriptor._pattern_2,
                    start, 'end', count=count, regexp=True)

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
                    b.sub_blocks += d.get_blocks(
                        text, b.index_start(), b.index_end())

        if last_blk.descriptor.type == 'toclosetoken' and \
                last_blk.state == 0 and \
                last_blk.descriptor.multi_line:
            return blks, last_blk.descriptor

        return blks, None

    def _purge(self, blks):
        if len(blks) in [0, 1]:
            return blks

        #print('*** PURGE')

        # order by start col
        n_blks = HighlightBlocks.order_blocks(blks)

        #print(len(n_blks))
        #for b in n_blks:
        #    print(b.descriptor.style)
        #    print(' ' + str(b.index_start()) + '-' + str(b.index_end()))

        # Verify if blocks intersects each other and delete
        res = []
        for b in n_blks:
            self._mark_for_delete(b, n_blks, res)

        #print('REMOVING ...')
        for r in res:
            #print(r)
            n_blks.remove(r)

        #for b in n_blks:
        #    print(b.descriptor.style)
        #    print(' ' + str(b.index_start()) + '-' + str(b.index_end()))
        #print(len(n_blks))

        return n_blks

    def _mark_for_delete(self, block, blks, found):
        if block in found:
            return
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
                descriptor.is_separator = self._is_separator
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
        self.is_separator = None

        self.type = self.type.lower()
        types = [
                'wholeword',
                'toclosetoken',
                'toeol',
                'regex'
            ]
        if self.type not in types:
            raise Exception("Ivalid descriptor type: '{0}'".format(self.type))

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
                if self.type in {'wholeword', 'regex', 'toeol'}:
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
                            descriptor=self,
                        )
                    )
                if self.type == 'toeol':
                    # Search for
                    # other 'ToEOL' blocks
                    end_index = text.index(
                        '{0}+{1}c'.format(index, len(self._tokens[0].value)))
                text.mark_set('startIndex', end_index)

        return blocks

    def _to_close_token_open_search(self, text, start, end, count):
        '''
        This function finds a match for the 'ToCloseToken' descriptor when
        close_token is not in same line.
        Return a tuple: [startIndex, endIndex]
        '''

        if self.type not in {'toclosetoken',}:
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
        
        if self.type == 'wholeword':
            for token in self._tokens:
                if pattern != '':
                    pattern += '|'
                pattern += token.value
            if pattern != '':
                pattern = r'\y(' + pattern + r')\y'

        elif self.type == 'regex':
            pattern = self._tokens[0].value

        elif self.type == 'toeol':
            pattern = self._tokens[0].value
            pattern += r'.*'

        elif self.type == 'toclosetoken':
            pattern = self._tokens[0].value
            pattern += r'(.*?)'
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
                if descriptor.multi_line:
                    raise Exception("Sub descriptor can not be 'Multiline'")
                descriptor.is_separator = self.is_separator
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
