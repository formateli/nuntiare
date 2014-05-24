# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys

class ReportItemsInfo():
    def __init__(self, element, parent):
        self.item_list=[]     
        self.total_height = 0
        self.min_height = sys.float_info.max
        self.max_height = 0
        self.can_grow=False
        self.can_shrink=False
        
        items = element.get_element("ReportItems")
        if items:
            from . import page_item_factory
            for it in items.reportitems_list:
                page_item = page_item_factory(it, parent)
                self.total_height = self.total_height + page_item.height 
                if page_item.height > self.max_height:
                    self.max_height =  page_item.height
                if page_item.height < self.min_height:
                    self.min_height =  page_item.height
                if page_item.type == "PageText":
                    if page_item.can_grow:
                        self.can_grow = True
                    if page_item.can_shrink:
                        self.can_shrink = True
                self.item_list.append(page_item)
                
