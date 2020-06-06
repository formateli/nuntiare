# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ttkwidgets import AutoHideScrollbar


class FrameScrolled(ttk.Frame):
    def __init__(self, parent):
        super(FrameScrolled, self).__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Horizontal (x) Scroll bar
        self.xscrollbar = AutoHideScrollbar(self, orient=tk.HORIZONTAL)
        self.xscrollbar.grid(row=1, column=0, sticky='ew')

        # Vertical (y) Scroll Bar
        self.yscrollbar = AutoHideScrollbar(self, orient=tk.VERTICAL)
        self.yscrollbar.grid(row=0, column=1, sticky='ns')


class PanedView(ttk.PanedWindow):
    def __init__(self, view):
        self.view = view
        self.type = None
        self.has_changed = False

        super(PanedView, self).__init__(view.notebook, orient=tk.HORIZONTAL)
        self.grid(row=0, column=0, sticky='wens')

        self.left_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.add(self.left_window, weight=4)
        self.right_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.add(self.right_window, weight=1)

        self._init_class()
        self._right_hidden = False

    def selected(self):
        raise NotImplementedError(
                "'selected' must be "
                "implemente by '{}'".format(self.__class__.__name__))

    def deselected(self):
        raise NotImplementedError(
                "'deselected' must be "
                "implemente by '{}'".format(self.__class__.__name__))

    def close(self):
        raise NotImplementedError(
                "'close' must be "
                "implemente by '{}'".format(self.__class__.__name__))

    def toggle_right_pane(self):
        if self._right_hidden:
            self.add(self.right_window, weight=1)
        else:
            self.forget(1)
        self._right_hidden = not self._right_hidden

    def get_frame(self):
        return FrameScrolled(self.view.notebook)

    def _init_class(self):
        raise NotImplementedError(
                "'_init_class' must be "
                "implemente by '{}'".format(self.__class__.__name__))
