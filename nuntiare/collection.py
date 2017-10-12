# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . import LOGGER


class CollectionItem(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def get_value(self):
        return self.value


class Collection(object):
    def __init__(self):
        self._items = []
        self._items_dict = {}

    def add_item(self, item):
        if item.name in self._items_dict:
            LOGGER.error(
                "Item '{0}' already exists in Collection '{1}'".format(
                    item.name, self.__class__.__name__), True)
        self._items.append(item)
        self._items_dict[item.name] = item

    def __getattr__(self, name):
        if name in self._items_dict:
            return self._items_dict[name].get_value()
        LOGGER.error(
            "Item '{0}' not found in Collection '{1}'".format(
                name, self.__class__.__name__), True)

    def __call__(self, name, function):
        if name not in self._items_dict:
            LOGGER.error(
                "Item '{0}' not found in Collection '{1}'".format(
                    name, self.__class__.__name__), True)

        item = self._items_dict[name]

        if function == 'Name':
            return item.name
        if function == 'Value':
            return item.get_value()

    def __getitem__(self, key):
        if key in self._items_dict:
            return self._items_dict[key].get_value()
        if isinstance(key, int):
            if key > -1 and key < len(self._items):
                return self._items[key].get_value()
        err_msg = "Item '{0}' not found in Collection '{1}'. " \
            "Valid values: {2}"
        LOGGER.error(err_msg.format(
            key, self.__class__.__name__, self._items_dict.keys()), True)

    def __setitem__(self, key, value):
        if key not in self._items_dict:
            err_msg = "Item '{0}' not found in Collection '{1}'. " \
                "Valid values: {2}"
            LOGGER.error(err_msg.format(
                key, self.__class__.__name__, self._items_dict.keys()), True)
        self._items_dict[key].value = value
