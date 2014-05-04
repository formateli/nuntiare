# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..element import Element
from ..enum import Enum

class SortDirection(Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }
    def __init__(self, report, expression):
        super(SortDirection, self).__init__(report, 'SortDirection', expression, SortDirection.enum_list)


class Sorting(Element):
    def __init__(self, node, lnk):
        elements={'SortBy': [Element.ELEMENT],}
        self.sortby_list=[]
        super(Sorting, self).__init__(node, elements, lnk)


class SortBy(Element):
    def __init__(self, node, lnk):
        elements={'SortExpression': [Element.VARIANT],
                  'SortDirection': [Element.ENUM],
                 }
        super(SortBy, self).__init__(node, elements, lnk)
        lnk.parent.sortby_list.append(self)

