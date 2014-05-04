# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

def get_report_items(element, parent):
    item_list = []

    items = element.get_element("ReportItems")
    if not items:
        return item_list

    from . import page_item_factory

    for it in items.reportitems_list:
        page_item = page_item_factory(it)
        page_item.parent = parent
        item_list.append(page_item)

    return item_list

