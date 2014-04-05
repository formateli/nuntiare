# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Sorting(Element):
    def __init__(self, node, lnk):
        elements={'SortBy': [Element.ELEMENT],}
        super(Sorting, self).__init__(node, elements, lnk)


class SortBy(Element):
    def __init__(self, node, lnk):
        elements={'SortExpression': [Element.VARIANT],
                  'Direction': [Element.ENUM],
                 }
        super(SortBy, self).__init__(node, elements, lnk)


class Direction(Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }

    def __init__(self, expression):
        super(Direction, self).__init__('Direction', expression, Direction.enum_list)

