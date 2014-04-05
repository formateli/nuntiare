# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Grouping(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'GroupExpressions': [Element.ELEMENT],
                  'PageBreakAtStart': [Element.BOOLEAN],
                  'PageBreakAtEnd': [Element.BOOLEAN],
                  'Filters': [Element.ELEMENT],
                  'Parent': [Element.VARIANT],
                 }
        super(Grouping, self).__init__(node, elements, lnk)


class GroupExpressions(Element):
    def __init__(self, node, lnk):
        elements={'GroupExpression': [Element.STRING],}
        super(GroupExpressions, self).__init__(node, elements, lnk)

