# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.


class Filters(Element):
    def __init__(self, node, lnk):
        elements={'Filter': [Element.ELEMENT],}
        self.filter_list=[]
        super(Filters, self).__init__(node, elements, lnk)


class Filter(Element):
    def __init__(self, node, lnk):
        elements={'FilterExpression': [Element.VARIANT],
                  'Operator': [Element.STRING],
                  'FilterValues': [Element.ELEMENT],
                 }
        super(Filter, self).__init__(node, elements, lnk)
        lnk.parent.filter_list.append(self)


class FilterValues(Element):
    def __init__(self, node, lnk):
        elements={'FilterValue': [Element.VARIANT],}
        super(FilterValues, self).__init__(node, elements, lnk)

