# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. types.element import Element
from .. types.enum import Enum

class SortDirection(Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }
    def __init__(self, expression):
        super(SortDirection, self).__init__('SortDirection', expression, SortDirection.enum_list)


class SortExpressions(Element):
    def __init__(self, node, lnk):
        elements={'SortExpression': [Element.ELEMENT],}
        self.sortby_list=[]
        super(SortExpressions, self).__init__(node, elements, lnk)


class SortExpression(Element):
    def __init__(self, node, lnk):
        elements={'Value': [Element.VARIANT],
                  'Direction': [Element.ENUM, 'SortDirection'],
                 }
        super(SortExpression, self).__init__(node, elements, lnk)
        lnk.parent.sortby_list.append(self)

