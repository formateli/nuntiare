# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. import logger
from ..tools import raise_error_with_log

class Element(object):
    ELEMENT=0
    STRING=1
    INTEGER=2
    BOOLEAN=3
    SIZE=4
    COLOR=5
    EXPRESSION=6
    EXPRESSION_LIST=7
    URL=8
    ENUM=9
    VARIANT=90

    def __init__(self, node, elements, lnk):

        lnk.obj=self
        self.element_list={}      # Here we list elements found for this element
        self.reportitems_list=[]  # report items list. Only if it is a ReportItems element
        self.lnk=lnk              # This is the linking object. See link.py

        import factory #--> Loading here we avoid circular references

        items_by_name={}

        for n in node.childNodes:
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
            if elements[n.nodeName][0] == Element.ELEMENT:
                el = factory.get_element(n.nodeName, n, lnk)
                if n.nodeName in ("Line", "Rectangle", "Textbox", "Image", "Subreport",
                            "CustomReportItem", "Grid", "Table"):
                    if n.nodeName in ("Textbox"): 
                        if lnk.report.report_items.has_key(el.name):
                            raise_error_with_log("Report already has a Texbox with name '{0}'".format(el.name))
                        else:
                            lnk.report.report_items[el.name] = el
                    if items_by_name.has_key(el.name):
                        raise_error_with_log("The container already has a report item with name '{0}'".format(el.name))
                    items_by_name[el.name]=el
                else:
                    self.element_list[n.nodeName] = el
            elif elements[n.nodeName][0]==Element.ENUM:
                if len(elements[n.nodeName])==1:
                    enum_name = n.nodeName
                else: 
                    enum_name = elements[n.nodeName][1]
                self.element_list[n.nodeName]=factory.get_enum(enum_name, n, lnk.report)
            elif elements[n.nodeName][0]==Element.EXPRESSION_LIST:
                ex_lst = factory.get_expression_list(n.nodeName, n, lnk)
                self.element_list[n.nodeName]=ex_lst
            else: 
                ex=factory.get_expression(elements[n.nodeName][0], n, lnk.report) 
                self.element_list[n.nodeName]=ex

        # Z Order
        if len(items_by_name) > 0:
            z_list=[]
            for key, it in items_by_name.items():
                l = (it.zindex, it)
                z_list.append(l)
            res = sorted(z_list, key=lambda z: z[0])
            for r in res:                
                self.reportitems_list.append(r[1])
    
    def get_element(self, name):
        if self.element_list.has_key(name):
            return self.element_list[name]

