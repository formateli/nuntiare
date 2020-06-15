# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ..common import PanedView, MementoCaretaker
from ..common.tools import get_size_px
from .xml_node import NuntiareXmlNode
from .property import NuntiareProperty
from .report_item import ReportItem, ElementStyle


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
        self._report_items = []

        self.info = ElementStyle(
                name, master._treeview)
        # Map update function
        self.info.update = self.update
        self._rec = None  # Canvas rectangle
        self.visible = False

        self.config(
                width=100, height=100,
                scrollregion=(0, 0, 100, 100))

    def add_report_item(self, name, tree_node, parent):
        report_item = ReportItem(
                name, self, self._master._treeview, parent)
        report_item.set_tree_item(tree_node)
        tw = self._master._treeview
        self._report_items.append(report_item)
        return report_item

    def remove_report_items(self, report_item):
        i = 0
        for ri in self._report_items:
            if ri == report_item:
                del self._report_items[i]
                break
            i += 1 

    def create_all(self):
        for ri in self._report_items:
            ri.create()

    def set_item(self, item):
        self.info.set_tree_item(item)

    def update(self, name_changed=None, type_=None):
        if self.info.item is None:
            return

        opts = {}
        opts['fill'] = self.info.Style.BackgroundColor
        borders = self.info.Style.get_borders()
        if borders['equal']:
            opts['outline'] = borders['TopBorder']['Color']
            opts['width'] = get_size_px(borders['TopBorder']['Width'])
            bs = borders['TopBorder']['BorderStyle']
            if bs == 'None':
                opts['width'] = 0
                opts['outline'] = None

        if self._rec is None:
            width = get_size_px(self._master.page_info.PageWidth)
            height = self.get_height()
            self._rec = self.create_rectangle(
                0, 0, width, height, **opts)
        else:
            if name_changed == 'Height':
                width = get_size_px(self._master.page_info.PageWidth)
                height = self.get_height()
                x1, y1, x2, y2 = self.coords(self._rec)
                self.coords(
                    self._rec, 0, 0, width, height)
                self.config(
                    width=width, height=height,
                    scrollregion=(0, 0, width, height))

                # Update Body Height
                if self.info.name != 'Body':
                    self._master.get_section('Body').update('Height')
            else:
                self.itemconfig(self._rec, **opts)

    def _set_sash_pos(self):
        height = self.get_height()
        sash_index = self._get_sash_index()

        if sash_index is None:
            return  # Body
        if self.info.name == 'PageHeader':             
            sash_height = height
        else:
            sash_height = self._master.winfo_height() \
                - height
        self._master.sashpos(sash_index, sash_height)

    def _get_sash_index(self):
        count = len(self._master.panes())

        if count == 1:
            # It must be Body
            return
        elif count == 3:
            if self.info.name == 'PageHeader':
                return 0
            elif  self.info.name == 'PageFooter':
                return 1
            else:
                return
        else:
            if self.info.name == 'PageHeader':
                return 0
            elif  self.info.name == 'PageFooter':
                return 0
            else:
                return

    def get_height(self):
        if self.info is None or self.info.item is None:
            return 0

        if self.info.name == 'Body':
            height = get_size_px(self._master.page_info.PageHeight) \
                - self._master._sections['PageHeader'].get_height() \
                - self._master._sections['PageFooter'].get_height()
        else:
            height = get_size_px(self.info.Height)

        return height

    def add_object(self, obj, report_item):
        self._objects_2_ritems[obj] = report_item

    def get_report_item_from_object(self, obj):
        if self._objects_2_ritems[obj]:
            return self._objects_2_ritems[obj]


class Sections(ttk.PanedWindow):
    def __init__(self, master):
        super(Sections, self).__init__(master, orient=tk.VERTICAL)
        self.grid(row=0, column=0, sticky='wens')

        self.page_info = None
        self._treeview = None
        self._sections = {
            'PageHeader': None,
            'Body': None,
            'PageFooter': None,
            }

    def add_report_item(self, name, tree_node):
        section, parent = \
            self._treeview.get_report_item_info(tree_node)
        return self._sections[section].add_report_item(
            name, tree_node, parent)

    def set_treeview(self, treeview):
        self._treeview = treeview
        self.page_info = ElementStyle(
                'Page', treeview)

    def set_page_item(self, item):
        self.page_info.set_tree_item(item)

    def update():
        pass

    def create_section(self, name, frame):
        section = Section(
            name, self, frame,
            xscrollcommand=frame.xscrollbar.set,
            yscrollcommand=frame.yscrollbar.set)
        section.grid(row=0, column=0, sticky='wens')
        frame.xscrollbar.config(command=section.xview)
        frame.yscrollbar.config(command=section.yview)
        self._sections[name] = section

    def get_section(self, name):
        return self._sections[name]

    def create_all(self):
        self.show_section()
        for _, section in self._sections.items():
            section.create_all()

    def show_section(self, name=None):
        if name is None:
            for key, _ in self._sections.items():
                self._show_section(key)
        else:
            self._show_section(name)

    def _show_section(self, name):
        section = self._sections[name]
        if section.info.item is None:
            if section.visible:
                self.forget(section.frame)
                section.visible = False
        else:
            if not section.visible:
                self.add(section.frame, weight=1)
                section.visible = True

            width = get_size_px(self.page_info.PageWidth)
            if name in ('PageHeader', 'PageFooter'):
                height = get_size_px(section.info.Height)
            else:
                t_height = self._sections['PageHeader'].get_height()
                b_height = self._sections['PageFooter'].get_height()
                height = get_size_px(self.page_info.PageHeight) \
                    - t_height - b_height

            section.config(
                width=width, height=height,
                scrollregion=(0, 0, width, height))

            section.update()

            count = len(self.panes())
            if count == 2:
                header = self.get_section('PageHeader')
                if header.info.item is not None:
                    self.insert(
                        0, self.get_section('PageHeader').frame, weight=1)
                    self.insert(
                        1, self.get_section('Body').frame, weight=1)
                else:
                    self.insert(
                        0, self.get_section('Body').frame, weight=1)
                    self.insert(
                        1, self.get_section('PageFooter').frame, weight=1)
            elif count == 3:
                self.insert(
                    0, self.get_section('PageHeader').frame, weight=1)
                self.insert(
                    1, self.get_section('Body').frame, weight=1)
                self.insert(
                    2, self.get_section('PageFooter').frame, weight=1)

            self.after(500, lambda: section._set_sash_pos())


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
        prop = NuntiareProperty(r_prop_frame, self._xml)
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
            source = self._new_snipet()
            is_file = False
        else:
            source = self.view.full_file_name
        self._xml.parse(source, is_file)

        self.sections.create_all()

    @staticmethod
    def _new_snipet():
        xml = '<Nuntiare><Name>New Report</Name><Page/>' \
            '<Body><ReportItems/></Body></Nuntiare>'
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
