# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data_region import DataRegion
from ...element import Element

class Table(DataRegion):
    def __init__(self, node, lnk):
        elements={'TableColumns': [Element.ELEMENT],
                  'TableHeader': [Element.ELEMENT],
                  'TableGroups': [Element.ELEMENT],
                  'TableDetails': [Element.ELEMENT],
                  'TableFooter': [Element.ELEMENT],
                  'FillPage': [Element.BOOLEAN],
                 }
        super(Table, self).__init__(node, lnk, elements)


class TableColumns(Element):
    def __init__(self, node, lnk):
        elements={'TableColumn': [Element.ELEMENT],}
        self.column_list=[]
        super(TableColumns, self).__init__(node, elements, lnk)


class TableColumn(Element):
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableColumn, self).__init__(node, elements, lnk)
        lnk.parent.column_list.append(self)


class TableColumn(Element):
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableColumn, self).__init__(node, elements, lnk)
        lnk.parent.column_list.append(self)


class TableHeader(Element):
    def __init__(self, node, lnk):
        elements={'TableRows': [Element.ELEMENT],
                  'RepeatOnNewPage': [Element.BOOLEAN],
                 }
        super(TableHeader, self).__init__(node, elements, lnk)


class TableFooter(Element):
    def __init__(self, node, lnk):
        elements={'TableRows': [Element.ELEMENT],
                  'RepeatOnNewPage': [Element.BOOLEAN],
                 }
        super(TableFooter, self).__init__(node, elements, lnk)


class TableDetails(Element):
    def __init__(self, node, lnk):
        elements={'TableRows': [Element.ELEMENT],
                  'Grouping ': [Element.ELEMENT],
                  'Sorting': [Element.ELEMENT],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableDetails, self).__init__(node, elements, lnk)


class TableRows(Element):
    def __init__(self, node, lnk):
        elements={'TableRow': [Element.ELEMENT],}
        self.row_list=[]
        super(TableRows, self).__init__(node, elements, lnk)


class TableRow(Element):
    def __init__(self, node, lnk):
        elements={'TableCells': [Element.ELEMENT],
                  'Height': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableRow, self).__init__(node, elements, lnk)
        lnk.parent.row_list.append(self)


class TableCells(Element):
    def __init__(self, node, lnk):
        elements={'TableCell': [Element.ELEMENT],}
        self.cell_list=[]
        super(TableCells, self).__init__(node, elements, lnk)


class TableCell(Element):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'ColSpan': [Element.INTEGER],
                 }
        super(TableCell, self).__init__(node, elements, lnk)
        lnk.parent.cell_list.append(self)


class TableGroups(Element):
    def __init__(self, node, lnk):
        elements={'TableGroup': [Element.ELEMENT],}
        self.group_list=[]
        super(TableGroups, self).__init__(node, elements, lnk)


class TableGroup(Element):
    def __init__(self, node, lnk):
        elements={'Grouping ': [Element.ELEMENT],
                  'Sorting': [Element.ELEMENT],
                  'GroupHeader': [Element.ELEMENT],
                  'GroupFooter': [Element.ELEMENT],
                  'Visibility': [Element.ELEMENT],
                 }
        super(TableGroup, self).__init__(node, elements, lnk)
        lnk.parent.group_list.append(self)

