# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page_item import PageLine, PageRectangle, PageText
from page_grid import PageGrid, PageTable
from ..tools import raise_error_with_log

def page_item_factory(it, parent):
    page_item = None
    if it.type == "Line":
        page_item = PageLine(it, parent)
    if it.type == "Rectangle":
        page_item = PageRectangle(it, parent)
    if it.type == "Textbox":
        page_item = PageText(it, parent)
    if it.type == "Grid":
        page_item = PageGrid(it, parent)
    if it.type == "Table":
        page_item = PageTable(it, parent)

    if not page_item:
        raise_error_with_log("Error trying to get Report item. Invalid definition element '{0}'".format(it))

    return page_item

