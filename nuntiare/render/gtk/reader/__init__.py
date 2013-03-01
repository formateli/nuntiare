# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import gtk
from gtk_reader import GtkReader

def render(report):
    GtkReader(report)

def get_help():
    return 'Here the module help'
