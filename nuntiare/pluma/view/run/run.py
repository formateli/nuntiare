# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
import logging
from nuntiare import LOGGER
from nuntiare.report import Report
from nuntiare.render.render import Render
from ...materialtheme.widgets import GroupToolBarTheme as GroupToolBar
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

        # TODO destroy menu when pluma.tab close

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

    _handler = None

    def __init__(self, parent, xscrollcommand, yscrollcommand):
        fnt = tk.font.Font(family='Courier New', size=12)
        super(LogWindow, self).__init__(parent, wrap=tk.NONE,
                                        font=fnt,
                                        xscrollcommand=xscrollcommand,
                                        yscrollcommand=yscrollcommand,
                                        bg='black', fg='white',
                                        state=tk.DISABLED)
        LogWindow._set_log_handler()

    def clear(self):
        self.config(state=tk.NORMAL)
        self.delete(1.0, 'end')
        self.config(state=tk.DISABLED)
        LogWindow._handler.setStream(self)

    def critical(self, e):
        LOGGER.critical("Pluma error while procesing report. {0}".format(e))

    def write(self, txt):
        self.config(state=tk.NORMAL)
        self.insert('insert', txt)
        self.see('insert')
        self.update_idletasks()

    def flush(self):
        self.config(state=tk.DISABLED)

    @classmethod
    def _set_log_handler(cls):
        if cls._handler is None:
            cls._handler = logging.StreamHandler()
            LOGGER.add_handler(
                    cls._handler,
                    level='DEBUG',
                    formatter='%(levelname)s: %(message)s')


class RunView(PanedView):

    _title = None

    def __init__(self, view):
        super(RunView, self).__init__(view)
        self.type = 'run'

        up_frame = self.get_frame()
        self._canvas = tk.Canvas(
            up_frame,
            xscrollcommand=up_frame.xscrollbar.set,
            yscrollcommand=up_frame.yscrollbar.set)
        self._canvas.grid(row=0, column=0, sticky='wens')
        self.left_window.add(up_frame, weight=3)
        up_frame.xscrollbar.config(command=self._canvas.xview)
        up_frame.yscrollbar.config(command=self._canvas.yview)

        down_frame = self.get_frame()
        self.log = LogWindow(
                down_frame,
                xscrollcommand=down_frame.xscrollbar.set,
                yscrollcommand=down_frame.yscrollbar.set)
        self.log.grid(row=0, column=0, sticky='wens')
        self.left_window.add(down_frame, weight=1)
        down_frame.xscrollbar.config(command=self.log.xview)
        down_frame.yscrollbar.config(command=self.log.yview)

        r_frame = self.get_frame()
        runbar = RunBar(r_frame, self)
        runbar.grid(row=0, column=0, sticky='wen')
        self.right_window.add(r_frame, weight=1)

    def run(self):
        self.log.clear()
        text = self.view.get_view('text')
        try:
            report = Report(text.text.get(1.0, tk.END))
            report.add_path(self.view.directory_name)
            report.run()

            self._canvas.config(
                    width=1000, height=1000,
                    scrollregion=(0, 0, 1000, 1000))

            render = Render.get_render('tk')
            render.render(report, self._canvas)
        except Exception as e:
            self.log.critical(e)
            return

    def selected(self):
        tb = self.view.pluma.toolbar
        tb.show('text', False)
        tb.show('undo_redo', False)

    def deselected(self):
        pass

    def close(self):
        pass

    def _init_class(self):
        if RunView._title is None:
            RunView._title = 'Run'
