# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare import logger
from nuntiare.tools import raise_error_with_log
from link import Link

class Element(object):
    NAME=0
    ELEMENT=1
    STRING=2
    INTEGER=3
    BOOLEAN=4
    SIZE=5
    COLOR=6
    EXPRESSION=7
    URL=8
    ENUM=9
    LANGUAGE=10
    VARIANT=11

    def __init__(self, node, elements, lnk):

        lnk.obj=self
        self.element_list={}      # Here we list elements found for this element
        self.reportitems_list={}  # report items list. Only if it is a ReportItems element
        self.lnk=lnk              # This is the linking object. See link.py

        import factory #--> Loading here we avoid circular references

        for n in node.childNodes:
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
            if elements[n.nodeName][0] == Element.ELEMENT:
                el = factory.get_element(n.nodeName, n, lnk)
                if n.nodeName in ("Line","Rectangle","Textbox","Image","Subreport","CustomReportItem","Grid"):
                    if self.reportitems_list.has_key(el.name):
                        raise_error_with_log("ReportItem '{0}' already exists. [{1}]".format(el.name, n.nodeName))
                    if n.nodeName in ("Textbox"): 
                        if lnk.report.report_items.has_key(el.name):
                            raise_error_with_log("Report already has a Texbox with name '{0}'".format(el.name))
                        else:
                            lnk.report.report_items[el.name] = el
                    self.reportitems_list[el.name] = el
                else:
                    self.element_list[n.nodeName] = el
            elif elements[n.nodeName][0]==Element.ENUM:
                self.element_list[n.nodeName]=factory.get_enum(elements[n.nodeName][1], n)
            else: 
                self.element_list[n.nodeName]=factory.get_expression(elements[n.nodeName][0], n)
    
        if len(self.reportitems_list) > 0:
            # Sort by ZIndex
            zlist={}
            for key, value in self.reportitems_list.items():
                zlist[key]=value.zindex
            res=sorted(zlist.items(), key=lambda z: z[1]) 
            newlist={}
            for r in res:
                newlist[r[0]] = self.reportitems_list[r[0]]
            self.reportitems_list = {}
            self.reportitems_list = newlist.copy()

    def get_element(self, name):
        if self.element_list.has_key(name):
            return self.element_list[name]

