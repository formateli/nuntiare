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

    def apply_hl(self, text, text_info, blocks):
        first_time = not text.tags_setted
        if first_time:
            text.set_tags(self._styles)

        if first_time:
            self._apply_hl_first_time(text, blocks)
        else:
            self._apply_hl_text_changed(text, text_info, blocks)

    def _apply_hl_first_time(self, text, blocks):
        #TODO must be line by line
        for d in self._descriptors:
            d.apply_regex(text, text.index('1.0'), text.index('end'))

    def _apply_hl_text_changed(self, text, text_info, blocks):
        pass

    def _process_line(self, text, txt, line_no, blocks):
        start_index = '{0}.{1}'.format(line_no, 0)
        end_index = '{0}.{1}'.format(line_no, len(txt))
        blks = []
        for d in self._descriptors:
            blks += d.get_blocks(text, start_index, end_index)

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
        self._type = self.get_attr_value(
                node, 'type', None, True)
        self._style = self.get_attr_value(
                node, 'style', None, True)
        self._multi_line = bool(self.get_attr_value(
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

    def get_blocks(self, text, start, end, prefix=''):
        if not self._pattern:
            return

        blocks = []

        matchStart = prefix + 'matchStart'
        matchEnd = prefix + 'matchEnd'
        searchLimit = prefix + 'searchLimit'

        text.mark_set(matchStart, start)
        text.mark_set(matchEnd, start)
        text.mark_set(searchLimit, end)

        count = text.new_int_var()

        while True:
            index = text.search(self._pattern, matchEnd, searchLimit,
                                count=count, regexp=True)
            if index == '' or count.get() == 0:
                if self._type in {'WholeWord', 'ToEOL'}:
                    break
                else:
                    res_multiline = self._to_close_token_search(
                            text, matchEnd, searchLimit, count, prefix)
                    if not res_multiline:
                        break
                    self._apply_tag(text, res_multiline[0], res_multiline[1], prefix)
            else:
                end_index = text.index('{0}+{1}c'.format(index, count.get()))
                bloks.append(HighlightBlock(
                        index, 
                        end_index,
                        descriptor=self)
                    )
                text.mark_set(matchEnd, end_index)

            #if self._descriptors: # Sub descriptors
            #    for d in self._descriptors:
            #        d.apply_regex(text,
            #            text.index(matchStart), text.index(matchEnd + '-1c'),
            #            prefix='s')

        return blocks

    def apply_regex(self, text, start, end, prefix=''):
        if not self._pattern:
            return

        matchStart = prefix + 'matchStart'
        matchEnd = prefix + 'matchEnd'
        searchLimit = prefix + 'searchLimit'

        text.mark_set(matchStart, start)
        text.mark_set(matchEnd, start)
        text.mark_set(searchLimit, end)

        count = text.new_int_var()

        while True:
            index = text.search(self._pattern, matchEnd, searchLimit,
                                count=count, regexp=True)
            if index == '' or count.get() == 0:
                if self._type in {'WholeWord', 'ToEOL'}:
                    break
                else:
                    res_multiline = self._to_close_token_search(
                            text, matchEnd, searchLimit, count, prefix)
                    if not res_multiline:
                        break
                    self._apply_tag(text, res_multiline[0], res_multiline[1], prefix)
            else:
                self._apply_tag(text, index, count.get(), prefix)

            if self._descriptors: # Sub descriptors
                for d in self._descriptors:

                    d.apply_regex(text,
                        text.index(matchStart), text.index(matchEnd + '-1c'),
                        prefix='s')

    def _to_close_token_search(self, text, start, end, count, prefix):
        if self._type not in {'ToCloseToken',}:
            return

        index = text.search(self._pattern_1,
                    start, end, count=count, regexp=True)
        print('==========')
        print(self._pattern_1)
        print(self._multi_line)
        print(index)
        print(count.get())
        if index == '' or count.get() == 0:
            return

        multilineStart = prefix + 'multilineStart'
        multilineEnd = prefix + 'multilineEnd'

        start_index = index
        start_count = count.get()
        text.mark_set(multilineStart, index)

        if not self._multi_line:
            return [start_index, start_count] 

        index = text.search(self._pattern_2,
                    start, end, count=count, regexp=True)
        print(self._pattern_2)
        print(index)
        print(count.get())
        if index == '' or count.get() == 0:
            text.mark_set(multilineEnd, 'end')
        else:
            text.mark_set(multilineEnd, '{0}+{1}c'.format(index, count.get()))

        txt = text.get(multilineStart, multilineEnd)
        if txt:
            return [start_index, len(txt)]

    def apply_regex_BK(self, text, start, end, prefix=''):
        if not self._pattern:
            return

        matchStart = prefix + 'matchStart'
        matchEnd = prefix + 'matchEnd'
        searchLimit = prefix + 'searchLimit'

        text.mark_set(matchStart, start)
        text.mark_set(matchEnd, start)
        text.mark_set(searchLimit, end)

        count = text.new_int_var()

        while True:
            index = text.search(self._pattern, matchEnd, searchLimit,
                                count=count, regexp=True)
            if index == '' or count.get() == 0:
                if not self._multi_line:
                    break
                else:
                    res_multiline = self._get_multiline_search(
                            text, matchEnd, searchLimit, count, prefix)
                    if not res_multiline:
                        break
                    self._apply_tag(text, res_multiline[0], res_multiline[1], prefix)
            else:
                self._apply_tag(text, index, count.get(), prefix)

            if self._descriptors: # Sub descriptors
                for d in self._descriptors:
                    d.apply_regex(text,
                        text.index(matchStart), text.index(matchEnd + '-1c'),
                        prefix='s')

    def _get_multiline_search_XXX(self, text, start, end, count, prefix):
        if self._type != 'ToCloseToken':
            return

        index = text.search(self._pattern_1,
                    start, end, count=count, regexp=True)
        if index == '' or count.get() == 0:
            return

        multilineStart = prefix + 'multilineStart'
        multilineEnd = prefix + 'multilineEnd'

        start_index = index
        text.mark_set(multilineStart, index)

        index = text.search(self._pattern_2,
                    start, end, count=count, regexp=True)
        if index == '' or count.get() == 0:
            return

        text.mark_set(multilineEnd, '{0}+{1}c'.format(index, count.get()))

        txt = text.get(multilineStart, multilineEnd)
        if txt:
            return [start_index, len(txt)]

    def _apply_tag(self, text, index, count, prefix):
        matchStart = prefix + 'matchStart'
        matchEnd = prefix + 'matchEnd'

        text.mark_set(matchStart, index)
        text.mark_set(matchEnd, '%s+%sc' % (index, count))
        text.tag_add(self._style, matchStart, matchEnd)
        idx = text.index(matchEnd)
        text.mark_set(matchEnd, idx + '+1c')

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
        
        if self._type == 'WholeWord':
            for token in self._tokens:
                if pattern != '':
                    pattern += '|'
                pattern += token.value
            if pattern != '':
                pattern = r'\y(' + pattern + r')\y'

        elif self._type == 'ToEOL':
            pattern = self._tokens[0].value
            pattern += r'.*'

        elif self._type == 'ToCloseToken':
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
        self._blocks = []
        self._lines = []


class HighlightBlock():
    def __init__(self, start_index, end_index, descriptor, state='COMPLETED'):
        self._descriptor = descriptor
        self.state = state # OPEN, COMPLETED

        self._line_start, self._col_start = \
            self._get_line_col(start_index)
        self._line_end, self._col_end = \
            self._get_line_col(end_index)

    def _get_line_col(self, index):
        s = index.split('.')
        return s[0], s[1]
