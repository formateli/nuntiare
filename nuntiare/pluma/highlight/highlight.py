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

        files = os.listdir(DIR)
        for f in files:
            f = os.path.join(DIR, f)
            if os.path.isfile(f) and f.endswith('.xml'):
                doc = minidom.parse(f)
                root = doc.getElementsByTagName('highlightDefinition')
                if root:
                    self._add_def(root[0])

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

        self.case_sensitive = bool(self.get_attr_value(
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
                self._get_descriptors(n)

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

    def _get_descriptors(self, node):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'descriptor':
                descriptor = HighlightDescriptor(n)
                self._descriptors.append(descriptor)


class HighlightDescriptor(XmlMixin):
    def __init__(self, node):
        self._type = self.get_attr_value(
                node, 'type', None, True)
        self._style = self.get_attr_value(
                node, 'style', None, True)
        self._tokens = []

        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'tokens':
                self._add_tokens(n)

    def _add_tokens(self, node):
        for n in node.childNodes:
            if self.is_comment(n):
                continue
            if n.nodeName == 'token':
                token = HighlightToken(n)
                self._tokens.append(token)


class HighlightStyle(XmlMixin):
    def __init__(self, node):
        self.name = self.get_attr_value(
                node, 'name', None, True)
        self.fore_color = self.get_attr_value(
                node, 'foreColor', None)
        self.fore_color = bool(self.get_attr_value(
                node, 'bold', False))
        self.fore_color = bool(self.get_attr_value(
                node, 'italic', False))


class HighlightToken(XmlMixin):
    def __init__(self, node):
        self.value = self.get_attr_value(
                node, 'value', None, True)
        self.close_token = self.get_attr_value(
                node, 'closeToken', None)
        self.escape_token = self.get_attr_value(
                node, 'escapeToken', None)
        self.multiLine = bool(self.get_attr_value(
                node, 'multiLine', False))
