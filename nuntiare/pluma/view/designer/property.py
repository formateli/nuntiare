# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import tkinter as tk
from tkinter import ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
#from ttkwidgets.color import askcolor
from tkinter.colorchooser import askcolor
import nuntiare.definition.element as nuntiare_element
import nuntiare.definition.enum as nuntiare_enum


class _PropertyFrame(ttk.Frame):
    def __init__(self, master, root_window):
        super(_PropertyFrame, self).__init__(master)
        self._root_window = root_window
        self._bind_callbacks = {}

    def register_property_event(self, name):
        self._bind_callbacks = {name: []}

    def bind(self, event, callback):
        if event in self._bind_callbacks:
            self._bind_callbacks[event].append(callback)
        else:
            super(_PropertyFrame, self).bind(event, callback)

    def fire_event(self, event, data):
        callbacks = self._bind_callbacks[event]
        for cb in callbacks:
            cb(data)


class NuntiareProperty(_PropertyFrame):
    def __init__(self, master, treevew, root_window):
        super(NuntiareProperty, self).__init__(master, root_window)
        self._properties = {}
        self._row_count = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self._treevew = treevew
        self._item = None

        self.register_property_event('property_changed')

    def add_property(self, name, type_):
        if name not in self._properties:
            if type_ == nuntiare_element.Element.ENUM:
                property_ = PropertyEnum(
                    self, self._root_window, name, self._get_enum_list(name))
            elif type_ == nuntiare_element.Element.COLOR:
                property_ = PropertyColor(self, self._root_window, name)
            else:
                property_ = PropertyText(self, self._root_window, name)

            self._properties[name] = [
                    ttk.Label(self, text=name),
                    property_,
                ]
            property_.bind(
                'property_focusout', self._property_focusout)

        property_ = self._properties[name]
        property_[0].grid(
            row=self._row_count,
            column=0, sticky='wens',
            padx=2, pady=2)
        property_[1].grid(
            row=self._row_count,
            column=1, sticky='wens',
            padx=2, pady=2)
        self._row_count += 1
        return property_[1]

    def set_item(self, item):
        if item != self._item:
            self._item = item
            self.clear()

    def get_item(self):
        return self._item

    def clear(self):
        wgs = self.grid_slaves()
        for wg in wgs:
            wg.grid_forget()
        self._row_count = 0

    def _get_enum_list(self, name):
        enum = getattr(nuntiare_enum, name)
        return enum.enum_list

    def _property_focusout(self, property_):
        self.fire_event('property_changed', [self, property_])


class PropertyItem(_PropertyFrame):
    def __init__(self, master, root_window, name):
        super(PropertyItem, self).__init__(master, root_window)
        self.name = name
        self._value = None
        self._default = None

        self.register_property_event('property_focusout')
        self.bind('<FocusOut>', self._focusout)

    def set_value(self, value, default, force_value):
        self._value = value
        if force_value:
            self._value = None
        self._default = default
        self._clear_widget()
        if value is not None:
            self._set_widget_value(value)
        elif self._default is not None:
            self._set_widget_value('[Default: ' + str(self._default) + ']')

    def get_value(self):
        if self._value:
            return self._value
        if self._default:
            return self._default

    def _focusout(self, event):
        value = self._get_widget_value()
        if (self._value is None and not value) or \
                (value == self._value) or \
                (value.startswith('[Default: ') and value.endswith(']') or
                (not value and self._default is None)):
            return
        self._value = value
        self.fire_event('property_focusout', self)

    def _get_widget_value(self):
        raise NotImplementedError(
            "Function '_get_widget_value' must be implemented.")

    def _set_widget_value(self):
        raise NotImplementedError(
            "Function '_set_widget_value' must be implemented.")

    def _clear_widget(self):
        raise NotImplementedError(
            "Function '_clear_widget' must be implemented.")


class PropertyText(PropertyItem):
    def __init__(self, master, root_window, name):
        super(PropertyText, self).__init__(master, root_window, name)
        self._entry = ttk.Entry(self)
        self._entry.grid(row=0, column=0, sticky='wens')
        self.columnconfigure(0, weight=1)

    def _set_widget_value(self, value):
        self._entry.insert(0, value)

    def _get_widget_value(self):
        return self._entry.get()

    def _clear_widget(self):
        self._entry.delete(0, 'end')


class PropertyEnum(PropertyItem):
    def __init__(self, master, root_window, name, list_values):
        super(PropertyEnum, self).__init__(master, root_window, name)
        self._entry = AutocompleteCombobox(self,
                completevalues=list_values)
        self._entry.grid(row=0, column=0, sticky='wens')
        self.columnconfigure(0, weight=1)

    def _set_widget_value(self, value):
        self._entry.insert(0, value)

    def _get_widget_value(self):
        return self._entry.get()

    def _clear_widget(self):
        self._entry.delete(0, 'end')


class EntryModify(ttk.Entry):
    def __init__(self, master, **kwargs):
        self._var = StringVar()
        self._var.trace("w", self._text_changed)
        super(EntryModify, self).__init__(
                master, textvariable=self._var, **kwargs)

    def _text_changed(self):
        return self._var.get()


class PropertyColor(PropertyItem):
    def __init__(self, master, root_window, name):
        super(PropertyColor, self).__init__(master, root_window, name)

        self._var = tk.StringVar()
        self._var.trace("w", self._text_changed)
        self._entry = ttk.Entry(self, textvariable=self._var)
        self._entry.grid(row=0, column=0, sticky='wens')

        self._btn = ttk.Button(self)
        self._btn.grid(row=0, column=1, sticky='wens')
        self._btn.bind('<1>', self._choose_color)

        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=1)

    def _set_widget_value(self, value):
        self._entry.delete(0, 'end')
        self._entry.insert(0, value)
        st = self._style_by_color(value)
        self._btn.configure(style=st)

    def _get_widget_value(self):
        return self._entry.get()

    def _clear_widget(self):
        self._entry.delete(0, 'end')
        st = self._style_by_color(None)
        self._btn.configure(style=st)

    def _choose_color(self, event):
        color = self._entry.get()
        if color is not None and color.startswith('[Default: ') \
                and color.endswith(']'):
            color = color[10:len(color) - 1]

        res = askcolor(
            initialcolor=color,
            parent=self._root_window,
            title='Select a color')
        if not res[0]:
            return

        self._set_widget_value(res[1])

    def _text_changed(self, a, b, c):
        self._set_widget_value(self._entry.get())

    @staticmethod
    def _style_by_color(color):
        st_name = str(color) + '-property-color' + '.TButton'
        st = ttk.Style()
        st.configure(st_name, background=color)
        return st_name
