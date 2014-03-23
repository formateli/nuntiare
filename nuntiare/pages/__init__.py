# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from page import Pages

def get_pages(report):
    pages = Pages(report)
    pages.build_pages()
    return pages

