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
                print(extension)
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

    def apply_hl(self, text, text_info):
        first_time = not text.tags_setted
        if first_time:
            text.set_tags(self._styles)

        if first_time:
            self._apply_hl_first_time(text)
        else:
            self._apply_hl_text_changed(text, text_info)

    def _apply_hl_first_time(self, text):
        for d in self._descriptors:
            d.apply_regex(text)

    def _apply_hl_text_changed(self, text, text_info):
        pass

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
        self._multiLine = bool(self.get_attr_value(
                node, 'multiLine', False))
        self._tokens = []

        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'tokens':
                self._add_tokens(n)

        self._pattern, self._pattern_1, self._pattern_2 = \
                    self._get_pattern()

    def apply_regex(self, text):
        if not self._pattern:
            return

        start = text.index('1.0')
        end = text.index('end')
        text.mark_set("matchStart", start)
        text.mark_set("matchEnd", start)
        text.mark_set("searchLimit", end)

        count = text.new_int_var()
        multiline_count = 0
        while True:
            index = text.search(self._pattern, 'matchEnd', 'searchLimit',
                                count=count, regexp=True)
            if index == '' or count.get() == 0:
                if not self._multiLine:
                    break
                else:
                    if multiline_count == 0:
                        index = text.search(self._pattern_1,
                                'matchEnd', 'searchLimit',
                                count=count, regexp=True)
                        if index == '' or count.get() == 0:
                            break
                        multiline_count += 1
                        text.mark_set('matchStart', index)
                        continue
                    elif multiline_count == 1:
                        index = text.search(self._pattern_2,
                                'matchEnd', 'searchLimit',
                                count=count, regexp=True)
                        if index == '' or count.get() == 0:
                            text.mark_set('matchEnd', 'end')
                        else:
                            text.mark_set('matchEnd', index + '+' + str(len(self._tokens[0].close_token)) + 'c')

            text.mark_set('matchStart', index)
            text.mark_set('matchEnd', "%s+%sc" % (index, count.get()))
            text.tag_add(self._style, 'matchStart', 'matchEnd')

            multiline_count = 0

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
            pattern += r'.*'
            pattern += self._tokens[0].close_token
            pattern_1 = self._tokens[0].value + r'.*'
            pattern_2 = r'.*' + self._tokens[0].close_token

        return pattern, pattern_1, pattern_2


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
