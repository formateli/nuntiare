# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ..common import PanedView, MementoCaretaker
from ..common.tools import get_size_px
from .xml_node import NuntiareXmlNode, NuntiareProperty
from .report_item import ReportItem, ReportItemAttribute
from nuntiare.report import Report


class Section(tk.Canvas):
    def __init__(self, name, master, master_widget,
                 xscrollcommand,
                 yscrollcommand):
        super(Section, self).__init__(
                master_widget, bg='#f2f2f2',
                xscrollcommand=master_widget.xscrollbar.set,
                yscrollcommand=master_widget.yscrollbar.set)
        self.grid(row=0, column=0, sticky='nsew')

        self._master = master

        self.frame = master_widget

        self._objects_2_ritems = {}
        self._ritems_2_objects = {}

        self._report_items = []
        self.info = ReportItemAttribute(
                name, master._treeview)

        self.config(
                width=100, height=100,
                scrollregion=(0, 0, 100, 100))

    def add_report_item(self, name, tree_node, parent, meta):
        report_item = ReportItem(name, self, tree_node, parent, meta)

        tw = self._master._treeview
        self._report_items.append(report_item)
        return report_item

    def draw_all(self):
        for ri in self._report_items:
            ri.draw()

    def set_item(self, item):
        self.info.set_tree_item(item)
        self.info.set_style()

    def update(self):
        pass

    def add_object(self, obj, report_item):
        self._objects_2_ritems[obj] = report_item
        self._ritems_2_objects[report_item] = obj

    def get_object_from_report_item(self, report_item):
        if self._ritems_2_objects[report_item]:
            return self._ritems_2_objects[report_item]

    def get_report_item_from_object(self, obj):
        if self._objects_2_ritems[obj]:
            return self._objects_2_ritems[obj]

    def draw_rectangle_style(self, x1, y1, x2, y2, style):
        fill = style['color'] if style['color'] is not None else ''
        
        border = style['border']
        if border is not None:
            outline = style['border_color']
            border_style = style['border_style']
            border_width = style['border_width']

        if border:
            rec = self.create_rectangle(
                    x1, y1, x2, y2, fill=fill,
                    outline=outline, width=border_width)
        else:
            rec = self.create_rectangle(
                    x1, y1, x2, y2, fill=fill,
                    outline='', width=0)
            # TODO draw line per each border
        return rec


class Sections(ttk.PanedWindow):
    def __init__(self, master):
        super(Sections, self).__init__(master, orient=tk.VERTICAL)
        self.grid(row=0, column=0, sticky='wens')

        self._page_info = None
        self._treeview = None
        self._sections = {
            'PageHeader': None,
            'Body': None,
            'PageFooter': None,
            }

    def add_report_item(self, name, tree_node):
        section, parent, meta = \
            self._treeview.get_report_item_info(tree_node)
        return self._sections[section].add_report_item(
            name, tree_node, parent, meta)

    def set_treeview(self, treeview):
        self._treeview = treeview
        self._page_info = ReportItemAttribute(
                'Page', treeview)

    def set_page_item(self, item):
        self._page_info.set_tree_item(item)
        self._page_info.set_style()

    def update():
        pass

    def create_section(self, name, frame):
        section = Section(
            name, self, frame,
            xscrollcommand=frame.xscrollbar.set,
            yscrollcommand=frame.yscrollbar.set)
        section.grid(row=0, column=0, sticky='wens')
        self.add(frame, weight=1)
        frame.xscrollbar.config(command=section.xview)
        frame.yscrollbar.config(command=section.yview)
        self._sections[name] = section

    def get_section(self, name):
        return self._sections[name]

    def draw_all(self):
        self.show_section()
        for _, section in self._sections.items():
            section.draw_all()

    def show_section(self, name=None):
        if name is None:
            for key, _ in self._sections.items():
                self._show_section(key)
        else:
            self._show_section(name)

    def _show_section(self, name):
        section = self._sections[name]
        if section.info is None or section.info.item is None:
            self.forget(section.frame)
        else:
            width = get_size_px(self._page_info.PageWidth)
            if name in ('PageHeader', 'PageFooter'):
                height = get_size_px(section.info.Height)
            else:
                height = get_size_px(self._page_info.PageHeight)  # TODO

            section.config(
                width=width, height=height,
                scrollregion=(0, 0, width, height))


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
        self.sections.set_treeview(self._xml)
        self.sections.create_section('PageHeader', self.get_frame())
        self.sections.create_section('Body', self.get_frame())
        self.sections.create_section('PageFooter', self.get_frame())

        self._memento = MementoCaretaker()

        is_file = True
        if self.view.full_file_name is None:
            source = self.new_snipet()
            is_file = False
        else:
            source = self.view.full_file_name
        self._xml.parse(source, is_file)

        self.sections.draw_all()

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
