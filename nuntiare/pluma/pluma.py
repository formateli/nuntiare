# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
import os
from .widget import UITabsObserver, UITabs

DIR = os.path.dirname(os.path.realpath(__file__))


class PanedView(ttk.PanedWindow):
    def __init__(self, id_, root, tabs, file_name):
        self.id = id_
        self.widget = None
        self.tabs = tabs
        self.file_name = file_name

        super(PanedView, self).__init__(root, orient=HORIZONTAL)
        self.pack(fill=BOTH, expand=1)

        self.left_frame = ttk.Frame(root)
        self.left_frame.pack(fill=BOTH, expand=1)
        self.add(self.left_frame)

        # Horizontal (x) Scroll bar
        self.xscrollbar = ttk.Scrollbar(self.left_frame, orient=HORIZONTAL)
        self.xscrollbar.pack(side=BOTTOM, fill=X)

        # Vertical (y) Scroll Bar
        self.yscrollbar = ttk.Scrollbar(self.left_frame)
        self.yscrollbar.pack(side=RIGHT, fill=Y)

        self.right_frame = ttk.Frame(root)
        self.right_frame.pack(fill=BOTH, expand=1)
        self.add(self.right_frame)


class DesignEditor(PanedView):
    def __init__(self, id_, root, tabs, file_name):
        super(DesignEditor, self).__init__(id_, root, tabs, file_name)

        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class XmlEditor(PanedView):
    def __init__(self, id_, root, tabs, file_name):
        super(XmlEditor, self).__init__(id_, root, tabs, file_name)

        self.widget = Text(self.left_frame, wrap=NONE,
            xscrollcommand=self.xscrollbar.set,
            yscrollcommand=self.yscrollbar.set)
        self.widget.pack(fill=BOTH, expand=1)

        self.xscrollbar.config(command=self.widget.xview)
        self.yscrollbar.config(command=self.widget.yview)

        self.new_file()

    def new_file(self):
        if self.file_name is None:
            self.widget.insert(END, self.new_snipet())
        else:
            self.get_file_content()
            self.tabs.set_title(self.id, self.file_name)
            self.tabs.set_dirty(self.id, False)
            self.tabs.set_tooltip(self.id, self.file_name)

    def new_snipet(self):
        xml = '''<?xml version="1.0" ?>
<Nuntiare>
</Nuntiare>'''
        return xml

    def get_file_content(self):
        self.widget.delete(1.0, END)
        with open(self.file_name) as _file:
            self.widget.insert(1.0, _file.read())


class RunView(PanedView):
    def __init__(self, id_, root, tabs, file_name):
        super(RunView, self).__init__(id_, root, tabs, file_name)

        label = ttk.Label(self.left_frame, text='NOT IMPLEMENTED')
        label.pack(fill=BOTH, expand=1)


class NuntiareView(ttk.Frame):
    def __init__(self, id_, root, tabs, file_name):
        super(NuntiareView, self).__init__(root)

        self.id = id_
        notebook = ttk.Notebook(self)

        design = DesignEditor(id_, notebook, tabs, file_name)
        notebook.add(design, text='Designer')

        xml = XmlEditor(id_, notebook, tabs, file_name)
        notebook.add(xml, text='Xml')

        run = RunView(id_, notebook, tabs, file_name)
        notebook.add(run, text='Run...')

        notebook.pack(expand=1, fill="both")


class Pluma(UITabsObserver):
    def __init__(self):
        self.root = Tk()
        self.root.title("Pluma - Nuntiare Report Designer")
        self.root.geometry('500x500')

        ICON = os.path.join(DIR, 'images', '24x24')
        
        new_file_icon = PhotoImage(file=ICON + '/new_file.png')
        open_file_icon = PhotoImage(file=ICON + '/open_file.png')
        save_file_icon = PhotoImage(file=ICON + '/save.png')

        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New', accelerator='Ctrl+N', compound='left',
                              image=new_file_icon, underline=0, command=self.new_file)
        file_menu.add_command(label='Open', accelerator='Ctrl+O', compound='left',
                              image=open_file_icon, underline=0, command=self.open_file)
        file_menu.add_command(label='Save', accelerator='Ctrl+S',
                              compound='left', image=save_file_icon, underline=0, command=self.save)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=self.exit_editor)
        menu_bar.add_cascade(label='File', menu=file_menu)

        self.root.config(menu=menu_bar)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.tab_count = 1
        self.tabs = UITabs(self.root, self)
        self.tabs.grid(column=0, row=0, sticky='ew')

        self.views = {}

        self.root.mainloop()

    def handle_addtab(self, tabs, file_name=None):
        tabs.add(tabid=self.tab_count,
            title='Untitled ' + str(self.tab_count),
            dirty=True)
        view = NuntiareView(self.tab_count, self.root, tabs, file_name)
        view.grid(column=0, row=1, sticky='nwes')
        self.views[self.tab_count] = view
        self.tab_count += 1

    def handle_closetab(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()
            self.views[tabid].destroy()
            del self.views[tabid]
        tabs.remove(tabid)

    def tab_deselected(self, tabs, tabid):
        if tabid in self.views:
            self.views[tabid].grid_forget()

    def tab_selected(self, tabs, tabid):
        if tabid in self.views: 
            self.views[tabid].grid(column=0, row=1, sticky='nwes')

    def new_file(self, event=None):
        self.handle_addtab(self.tabs)

    def open_file(self, event=None):
        input_file_name = tkinter.filedialog.askopenfilename(
                    defaultextension=".txt",
                    filetypes=[("All Files", "*.*"), ("Xml Documents", "*.xml")])
        if input_file_name:
            self.handle_addtab(self.tabs, input_file_name)

    def save(self, event=None):
        pass

    def save_as(event=None):
        pass

    def exit_editor(self, event=None):
        if tkinter.messagebox.askokcancel("Quit?",
                "Do you want to QUIT for sure?\n Make sure you've saved your current work."):
            self.root.destroy()

    def run(self):
        self.root.mainloop()
        try:
            self.root.destroy()
        except:
            pass
