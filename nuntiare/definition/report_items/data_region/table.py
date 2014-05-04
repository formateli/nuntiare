# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data_region import DataRegion
from ...element import Element

class Table(DataRegion):
    def __init__(self, node, lnk):
        elements={'Columns': [Element.ELEMENT],
                  'Header': [Element.ELEMENT],
                  'TableGroups': [Element.ELEMENT],
                  'Details': [Element.ELEMENT],
                  'Footer': [Element.ELEMENT],
                  'FillPage': [Element.BOOLEAN],
                 }
        super(Table, self).__init__("Table", node, lnk, elements)


class Header(Element):
    def __init__(self, node, lnk):
        elements={'Rows': [Element.ELEMENT],
                  'RepeatOnNewPage': [Element.BOOLEAN],
                 }
        super(Header, self).__init__(node, elements, lnk)


class Footer(Element):
    def __init__(self, node, lnk):
        elements={'Rows': [Element.ELEMENT],
                  'RepeatOnNewPage': [Element.BOOLEAN],
                 }
        super(Footer, self).__init__(node, elements, lnk)


class Details(Element):
    def __init__(self, node, lnk):
        elements={'Rows': [Element.ELEMENT],
                  'Grouping ': [Element.ELEMENT],
                  'Sorting': [Element.ELEMENT],
                  'Visibility': [Element.ELEMENT],
                 }
        super(Details, self).__init__(node, elements, lnk)


class TableGroups(Element):
    def __init__(self, node, lnk):
        elements={'TableGroup': [Element.ELEMENT],}
        self.group_list=[]
        super(TableGroups, self).__init__(node, elements, lnk)


class TableGroup(Element):
    def __init__(self, node, lnk):
        elements={'Grouping': [Element.ELEMENT],
                  'Sorting': [Element.ELEMENT],
                  'Header': [Element.ELEMENT],
                  'Footer': [Element.ELEMENT],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableGroup, self).__init__(node, elements, lnk)
        lnk.parent.group_list.append(self)

