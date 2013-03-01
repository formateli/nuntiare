# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Page(object):
    def __init__(self):
        self.page_number = None
        self.page_items=[]

    def add(self, page_item):
        self.page_items.append(page_item)


