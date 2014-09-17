# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ... import logger
from ... tools import raise_error_with_log

class ExpressionList(object):
    def __init__(self, node, elements, lnk):

        if len(elements) == 0 or len(elements) > 1:
            raise_error_with_log("ElementList only can have one sub element type.")

        lnk.obj=self
        self.lnk=lnk

        from .. factory import get_expression

        self.expression_list=[]

        for n in node.childNodes:
            if not elements.has_key(n.nodeName):
                if n.nodeName not in ('#text', '#comment'):
                    logger.warn("Unknown xml element '{0}' for '{1}'. Ignored.".format(n.nodeName, lnk.obj.__class__.__name__))
                continue
            must_be_constant = False
            if len(elements[n.nodeName])>1:
                must_be_constant = elements[n.nodeName][1]                
            ex = get_expression(elements[n.nodeName][0], n, must_be_constant) 
            self.expression_list.append(ex)

