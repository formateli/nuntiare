# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ..common import PanedView, MementoCaretaker
from .xml_node import NuntiareXmlNode, NuntiareProperty
from nuntiare.report import Report


class Section(tk.Canvas):
    def __init__(self, master,
                 xscrollcommand,
                 yscrollcommand):
        super(Section, self).__init__(
                master, bg='white',
                xscrollcommand=master.xscrollbar.set,
                yscrollcommand=master.yscrollbar.set)
        self.grid(row=0, column=0, sticky='nsew')

        self.config(
                width=100, height=100,
                scrollregion=(0, 0, 100, 100))

    def set_size(self):
        pass


class Sections(ttk.PanedWindow):
    def __init__(self, master):
        super(Sections, self).__init__(master, orient=tk.VERTICAL)
        self.grid(row=0, column=0, sticky='wens')

        self.header = None
        self.body = None
        self.footer = None

    def create_header(self, frame):
        self.header = self._create_section(frame, 5)

    def create_body(self, frame):
        self.body = self._create_section(frame, 1)

    def create_footer(self, frame):
        self.footer = self._create_section(frame, 5)

    def set_header_size(width, height):
        pass

    def set_footer_size(width, height):
        pass

    def _set_body_size():
        pass

    def _create_section(self, frame, weight):
        section = Section(
            frame,
            xscrollcommand=frame.xscrollbar.set,
            yscrollcommand=frame.yscrollbar.set)
        section.grid(row=0, column=0, sticky='wens')
        self.add(frame, weight=weight)
        frame.xscrollbar.config(command=section.xview)
        frame.yscrollbar.config(command=section.yview)
        return section


class DesignerView(PanedView):

    _title = None

    def __init__(self, view):
        super(DesignerView, self).__init__(view)
        self.type = 'designer'

        frame = ttk.Frame(self.view.notebook)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.sections = Sections(frame)
        self.sections.grid(row=0, column=0, sticky='wens')
        self.left_window.add(frame, weight=1)

        self.sections.create_header(self.get_frame())
        self.sections.create_body(self.get_frame())
        self.sections.create_footer(self.get_frame())

        r_xml_frame = self.get_frame()
        self._xml = NuntiareXmlNode(
                r_xml_frame,
                self,
                xscrollcommand=r_xml_frame.xscrollbar.set,
                yscrollcommand=r_xml_frame.yscrollbar.set)
        self._xml.grid(
            row=0, column=0, sticky='wens')
        self.right_window.add(r_xml_frame, weight=1)
        r_xml_frame.xscrollbar.config(command=self._xml.xview)
        r_xml_frame.yscrollbar.config(command=self._xml.yview)

        r_prop_frame = self.get_frame()
        prop = NuntiareProperty(r_prop_frame)
        prop.grid(row=0, column=0, sticky='wens')
        self.right_window.add(r_prop_frame, weight=1)

        self._xml.set_property(prop)

        self._memento = MementoCaretaker()

        is_file = True
        if self.view.full_file_name is None:
            source = self.new_snipet()
            is_file = False
        else:
            source = self.view.full_file_name
        self._xml.parse(source, is_file)
        #self._load_definition()

    def _load_definition(self):
        if self.view.full_file_name is None:
            report = Report(self._new_snipet())
        else:
            report = Report(self.view.full_file_name)

    @staticmethod
    def _new_snipet():
        xml = '''<?xml version="1.0" ?>
<Nuntiare>
</Nuntiare>'''
        return xml

    def selected(self):
        tb = self.view.pluma.toolbar
        tb.show('undo_redo', True)
        self._update_toolbar()

    def deselected(self):
        pass

    def close(self):
        pass

    def _update_toolbar(self):
        tb = self.view.pluma.toolbar
        tb.set_command('undo_redo', 'undo', self._undo)
        tb.set_command('undo_redo', 'redo', self._redo)
        self._verify_undo_redo()

    def _clear_memento(self):
        self._memento.clear()
        self._verify_undo_redo()

    def _verify_undo_redo(self):
        tb = self.view.pluma.toolbar
        tb.enable('undo_redo', 'undo', self._memento.is_undo_possible())
        tb.enable('undo_redo', 'redo', self._memento.is_redo_possible())

    def _undo(self):
        pass

    def _redo(self):
        pass

    def _init_class(self):
        if DesignerView._title is None:
            DesignerView._title = 'Designer'

            tb = self.view.pluma.toolbar
            tb.add_toolbar('undo_redo', after='file')
            tb.add_toolbar_item(
                    'undo_redo', 'undo', None, 'undo-24px')
            tb.add_toolbar_item(
                    'undo_redo', 'redo', None, 'redo-24px')
            tb.show('undo_redo', False)
