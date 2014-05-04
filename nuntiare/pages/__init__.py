# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page import Pages
from page_item import PageLine, PageRectangle, PageText
from page_grid import PageGrid, PageTable
from ..tools import raise_error_with_log

def get_pages(report):
    pages = Pages(report)
    pages.build_pages()
    return pages

def page_item_factory(it):
    page_item = None
    if it.type == "Line":
        page_item = PageLine(it)
    if it.type == "Rectangle":
        page_item = PageRectangle(it)
    if it.type == "Textbox":
        page_item = PageText(it)
    if it.type == "Grid":
        page_item = PageGrid(it)
    if it.type == "Table":
        page_item = PageTable(it)

    if not page_item:
        raise_error_with_log("Error trying to get Report item. Invalid definition element '{0}'".format(it))

    return page_item

