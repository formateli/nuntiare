# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..element import Element
from ..expression_list import ExpressionList

class Grouping(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'GroupExpressions': [Element.EXPRESSION_LIST],
                  'PageBreakAtStart': [Element.BOOLEAN],
                  'PageBreakAtEnd': [Element.BOOLEAN],
                  'Filters': [Element.ELEMENT],
                  'Parent': [Element.VARIANT],
                 }
        super(Grouping, self).__init__(node, elements, lnk)


class GroupExpressions(ExpressionList):
    def __init__(self, node, lnk):
        elements={'GroupExpression': [Element.VARIANT],}
        super(GroupExpressions, self).__init__(node, elements, lnk)

