# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from tkinter import ttk
from ttkwidgets import OnOffButton
from . import WidgetThemeMixin


class OnOffButtonTheme(OnOffButton, WidgetThemeMixin):
    def __init__(self, master=None, **kwargs):
        OnOffButton.__init__(self, master, **kwargs)
        WidgetThemeMixin.__init__(self)

    def _on_theme_changed(self, theme):
        self.config(style=self._style_class)
