# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from tkinter import ttk
from ..common import PanedView


class RunView(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(RunView, self).__init__(
            id_, pluma, view, tabs)
        self.type = 'run'
        frame = self.get_frame()
        label = ttk.Label(frame, text='NOT IMPLEMENTED')
        label.grid(row=0, column=0, sticky='wens')
        self.left_window.add(frame, weight=1)

        #frame_l = self.get_frame()
        #log = LogWindow(frame_l)
        #log.grid(row=0, column=0, sticky='wens')
