# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... import logger
from ...tools import raise_error_with_log

class Element(object):
    ELEMENT=0
    STRING=1
    INTEGER=2
    BOOLEAN=3
    FLOAT=4
    SIZE=5
    DATE=6
    COLOR=7
    EXPRESSION=8
    EXPRESSION_LIST=9
    URL=10
    ENUM=11
    VARIANT=90

    def __init__(self, node, elements, lnk):

        lnk.obj=self
        self.element_list={}        # Here we list elements found for this element
        self.reportitems_list=[]    # Peers report items list.
        self.lnk=lnk                # This is the linking object. See link.py

        from .. import factory

        # Collect all report items, at the end, order by ZIndex or appears order
        items_by_name={}
        z_count=0

        for n in node.childNodes:
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
            if elements[n.nodeName][0] == Element.ELEMENT:
                el = factory.get_element(n.nodeName, n, lnk)
                if n.nodeName in ("Line", "Rectangle", "Textbox", "Image", "Subreport",
                            "CustomReportItem", "Tablix"):
                    if n.nodeName in ("Textbox"): 
                        if lnk.report_def.report_items.has_key(el.name):
                            raise_error_with_log("Report already has a Texbox with name '{0}'".format(el.name))
                        lnk.report_def.report_items[el.name] = el
                    if items_by_name.has_key(el.name):
                        raise_error_with_log("The container already has a report item with name '{0}'".format(el.name))
                    i=el.zindex if el.zindex>-1 else z_count
                    items_by_name[el.name]=[el, i]
                    z_count = z_count + 1
                self.element_list[n.nodeName] = el
            elif elements[n.nodeName][0]==Element.ENUM:
                if len(elements[n.nodeName])==1:
                    enum_name = n.nodeName
                else: 
                    enum_name = elements[n.nodeName][1]
                self.element_list[n.nodeName]=factory.get_enum(enum_name, n)
            elif elements[n.nodeName][0]==Element.EXPRESSION_LIST:
                ex_lst = factory.get_expression_list(n.nodeName, n, lnk)
                self.element_list[n.nodeName]=ex_lst
            else: 
                must_be_constant = False
                if len(elements[n.nodeName]) > 1:
                    must_be_constant = elements[n.nodeName][1]
                ex=factory.get_expression(elements[n.nodeName][0], n, must_be_constant) 
                self.element_list[n.nodeName]=ex

        # Z Order
        self.reportitems_list=[]
        if len(items_by_name) > 0:
            z_list=[]
            for key, it in items_by_name.items():
                l = (it[1], it[0]) # zindex, reportitem
                z_list.append(l)
            res = sorted(z_list, key=lambda z: z[0])
            for r in res:
                self.reportitems_list.append(r[1])
    
    def get_element(self, name):
        if self.element_list.has_key(name):
            return self.element_list[name]

