# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import os
from tkinter import ttk
from .designer import DesignerView
from .text import TextView
from .run import RunView


class NuntiareView(ttk.Frame):
    def __init__(self, id_, pluma, tabs, full_file_name):
        super(NuntiareView, self).__init__(pluma)
        self.id = id_
        self.pluma = pluma
        self.tabs = tabs
        self.full_file_name = full_file_name
        self.file_name = None
        self.extension = None
        if full_file_name is not None:
            self.file_name = os.path.basename(full_file_name)
            extension = self.file_name.split('.')
            if len(extension) > 1:
                self.extension = extension[1]
            tabs.set_title(id_, self.file_name)
            tabs.set_dirty(id_, False)
            tabs.set_tooltip(id_, self.full_file_name)

        self.notebook = ttk.Notebook(self)
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._views = [
            DesignerView(self),
            TextView(self),
            RunView(self)
        ]

        for view in self._views:
            self.notebook.add(view, text=view._title)

        self.current_view = self._views[0]  # designer
        self.last_view = None

        self.notebook.grid(row=0, column=0, sticky='ewns')
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def get_view(self, type_):
        for view in self._views:
            if view.type == type_:
                return view
        raise ValueError("View '{}' not found.".format(type_))

    def tab_changed(self, event):
        nb = event.widget
        name = nb.select()
        obj = nb.nametowidget(name)

        self.last_view = self.current_view
        self.current_view = obj
        self.update_views()

    def update_views(self):
        for view in self._views:
            if view.type == self.current_view.type:
                view.selected()
            else:
                view.deselected()
