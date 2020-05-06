# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from ..theme import Theme


class WidgetThemeMixin:
    '''
    Provide an Interface for theming changes
    '''
    def __init__(self):
        Theme.bind('theme_changed', self._on_theme_changed)

    def _on_theme_changed(self, theme):
        '''
        For non ttk styled widget (Ex, Canvas) or for widget that
        need to make special changes, like image colors.
        This function is called each time Theme changed,
        usally when Theme.set_theme() is called.
        Widget must implement this function and pass
        modificatons to its own config funtion
        '''
        raise NotImplementedError(
            "Function '_on_theme_changed' not implemented by derived class '{}'".format(
                self.__class__.__name__))
