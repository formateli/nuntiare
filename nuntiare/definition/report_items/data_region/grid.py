# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.report_items.report_item import ReportItem
from nuntiare.definition.element import Element

class Grid(ReportItem):
    def __init__(self, node, lnk):
        super(Grid, self).__init__(node, lnk)


class TableColumns(Element):
    def __init__(self, node, lnk):
        elements={'TableColumn': [Element.ELEMENT],}
        super(TableColumns, self).__init__(node, elements, lnk)


class TableColumn(Element):
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }

        super(TableColumn, self).__init__(node, elements, lnk)


class Details(Element):
    def __init__(self, node, lnk):
        elements={'TableRows': [Element.ELEMENT],
                  'Grouping': [Element.ELEMENT],
                  'Sorting': [Element.ELEMENT],
                  'Visibility': [Element.ELEMENT],
                 }
        super(Details, self).__init__(node, elements, lnk)


class TableRows(Element):
    def __init__(self, node, lnk):
        elements={'TableRow': [Element.ELEMENT],}
        super(TableRows, self).__init__(node, elements, lnk)


class TableRow(Element):
    def __init__(self, node, lnk):
        elements={'TableCells': [Element.ELEMENT],
                  'Height': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }

        super(TableRow, self).__init__(node, elements, lnk)


class TableCells(Element):
    def __init__(self, node, lnk):
        elements={'TableCell': [Element.ELEMENT],}
        super(TableCells, self).__init__(node, elements, lnk)


class TableCell(Element):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'ColSpan': [Element.INTEGER],
                 }

        super(TableCell, self).__init__(node, elements, lnk)






