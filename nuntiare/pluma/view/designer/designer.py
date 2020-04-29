# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from tkinter import ttk
from ..common import PanedView


class DesignerView(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(DesignerView, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'designer'
        frame = self.get_frame()
        label = ttk.Label(frame, text='NOT IMPLEMENTED')
        label.grid(row=0, column=0, sticky='wens')
        self.left_window.add(frame, weight=1)
