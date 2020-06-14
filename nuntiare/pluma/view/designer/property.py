# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from tkinter import ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
import nuntiare.definition.element as nuntiare_element
import nuntiare.definition.enum as nuntiare_enum


class _PropertyFrame(ttk.Frame):
    def __init__(self, master):
        super(_PropertyFrame, self).__init__(master)
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
    def __init__(self, master, treevew):
        super(NuntiareProperty, self).__init__(master)
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
                    self, name, self._get_enum_list(name))
            else:
                property_ = PropertyText(self, name)

            self._properties[name] = [
                    ttk.Label(self, text=name),
                    property_,
                ]
            property_.bind(
                'property_focusout', self._property_focusout)

        property_ = self._properties[name]
        property_[0].grid(row=self._row_count, column=0, sticky='wens')
        property_[1].grid(row=self._row_count, column=1, sticky='wens')
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
    def __init__(self, master, name):
        super(PropertyItem, self).__init__(master)
        self.name = name
        self._value = None
        self._default = None

        self.register_property_event('property_focusout')
        self.bind('<FocusOut>', self._focusout)

    def set_value(self, value, default):
        self._value = value
        self._default = default
        self._clear_widget()
        if value is not None:
            self._set_widget_value(self._value)
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
    def __init__(self, master, name):
        super(PropertyText, self).__init__(master, name)
        self._entry = ttk.Entry(self)
        self._entry.grid(row=0, column=0, sticky='wens')

    def _set_widget_value(self, value):
        self._entry.insert(0, value)

    def _get_widget_value(self):
        return self._entry.get()

    def _clear_widget(self):
        self._entry.delete(0, 'end')


class PropertyEnum(PropertyItem):
    def __init__(self, master, name, list_values):
        super(PropertyEnum, self).__init__(master, name)
        self._entry = AutocompleteCombobox(self,
                completevalues=list_values)
        self._entry.grid(row=0, column=0, sticky='wens')

    def _set_widget_value(self, value):
        self._entry.insert(0, value)

    def _get_widget_value(self):
        return self._entry.get()

    def _clear_widget(self):
        self._entry.delete(0, 'end')
