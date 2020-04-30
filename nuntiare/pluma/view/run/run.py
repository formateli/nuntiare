# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from nuntiare.report import Report
from nuntiare.render.render import Render
from materialtheme.widgets import GroupToolBarTheme as GroupToolBar
from ...menu_manager import MenuManager
from ..common import PanedView


class RunBar(GroupToolBar):

    _next_id = -1

    def __init__(self, parent, view):
        super(RunBar, self).__init__(parent, 26)

        self._view = view
        self._id = RunBar._get_next_id()
        prefix = str(self._id) + '_' 
        iz = '22x22'

        self.add_toolbar('run')
        self.add_toolbar_item(
                'run', 'run_report', self._run,
                'play_arrow-24px', image_size=iz)
        btn_menu = self.add_toolbar_item(
                'run', 'save', None, 'save_alt-24px',
                image_size=iz)
        btn_menu.bind('<Button-1>', self._show_renders_menu)

        self._renders_menu = MenuManager.new_menu(prefix + 'renders',
                                                  None, parent=self)
        MenuManager.add_command(
                prefix + 'renders', 'title', 'Save as...',
                None, None, image='save_alt-24px', state=tk.NORMAL)
        MenuManager.add_separator(prefix + 'renders')
        renders = ['html', 'pdf', 'xml', 'csv']
        i = 2
        for r in renders:
            self._renders_menu.insert_command(
                    i, label=r,
                    command=lambda x=r: self._run_render(x))
            i += 1


        #TODO destroy menu when pluma.tab close

    def _run(self):
        self._view.run()

    @classmethod
    def _get_next_id(cls):
        cls._next_id += 1
        return cls._next_id

    def _show_renders_menu(self, event):
        try:
            self._renders_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self._renders_menu.grab_release()

    def _run_render(self, render):
        print(render)


class LogWindow(tk.Text):
    def __init__(self, parent, xscrollcommand, yscrollcommand):
        fnt = tk.font.Font(family='Courier New', size=14)
        super(LogWindow, self).__init__(parent, wrap=tk.NONE,
                                        font=fnt,
                                        xscrollcommand=xscrollcommand,
                                        yscrollcommand=yscrollcommand,
                                        bg='black', fg='white')


class RunView(PanedView):
    def __init__(self, id_, pluma, view, tabs):
        super(RunView, self).__init__(id_, pluma, view, tabs)
        self.type = 'run'

        up_frame = self.get_frame()
        label = ttk.Label(up_frame, text='NOT IMPLEMENTED')
        label.grid(row=0, column=0, sticky='wens')
        self.left_window.add(up_frame, weight=4)

        down_frame = self.get_frame()
        log = LogWindow(
                down_frame,
                xscrollcommand=down_frame.xscrollbar.set,
                yscrollcommand=down_frame.yscrollbar.set)
        log.grid(row=0, column=0, sticky='wens')
        self.left_window.add(down_frame, weight=1)
        down_frame.xscrollbar.config(command=log.xview)
        down_frame.yscrollbar.config(command=log.yview)

        r_frame = self.get_frame()
        runbar = RunBar(r_frame, self)
        runbar.grid(row=0, column=0, sticky='wen')
        self.right_window.add(r_frame, weight=1)

    def run(self):
        text = self.view.get_view('text')
        report = Report(text.text.get(1.0, tk.END))
        report.run()
        render = Render.get_render('html')
        render.render(report, overwrite=True)
        print('Finished')