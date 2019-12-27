# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.


class HighlightDefinition():
    def __init__(self):
        self._styles = {}
        self._separators = []
        self._descriptors = []

    def add_style(self, name, fore_color, back_color, bold, italic):
        st = HighlightStyle(fore_color, back_color, bold, italic)
        self._styles[name] = st

    def add_separators(self, separators):
        self._separators += separators

    def add_descriptor(self, type_, style, tokens):
        des = HighlightDescriptor(
                type_=type_,
                style=self._styles[style],
            )
        des.add_tokens(tokens)
        self._descriptors.append(des)


class HighlightDescriptor():
    def __init__(self, type_, style):
        self._type = type_ # WholeWord, ToCloseToken, ToEOL
        self._style = style
        self._tokens = []

    def add_tokens(self, tokens):
        for token in tokens:
            tk = HighlightToken(
                    token['value'],
                    token['close'],
                    token['escape'],
                    token['multiLine'],
                )
            self._tokens.append(tk)


class HighlightStyle():
    def __init__(self, fore_color, back_color, bold, italic):
        self.fore_color = fore_color
        self.back_color = back_color
        self.bold = bold
        self.italic = italic


class HighlightToken():
    def __init__(self, value, close=None, escape=None, multiLine=False):
        self.value = value
        self.close = close
        self.escape = escape
        self.multiLine = multiLine