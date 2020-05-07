# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from .theme import Theme


class TkMaterialTheme(tk.Tk):
    def __init__(self):
        super(TkMaterialTheme, self).__init__()

    def set_theme(self, theme_name=None):
        Theme.set_theme(theme_name)
