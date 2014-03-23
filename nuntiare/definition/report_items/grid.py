# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.report_items.report_item import ReportItem
from nuntiare.definition.element import Element

class Grid(ReportItem):
    def __init__(self, node, lnk):
        elements={'Columns': [Element.ELEMENT],
                  'Rows': [Element.ELEMENT],
                 }
        super(Grid, self).__init__(node, lnk, elements)


class Columns(Element):
    def __init__(self, node, lnk):
        elements={'Column': [Element.ELEMENT],}
        super(Columns, self).__init__(node, elements, lnk)


class Column(Element):
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }
        super(Column, self).__init__(node, elements, lnk)


class Rows(Element):
    def __init__(self, node, lnk):
        elements={'Row': [Element.ELEMENT],}
        super(Rows, self).__init__(node, elements, lnk)


class Row(Element):
    def __init__(self, node, lnk):
        elements={'Cells': [Element.ELEMENT],
                  'Height': [Element.SIZE],
                  'Visibility': [Element.ELEMENT],
                 }
        super(Row, self).__init__(node, elements, lnk)


class Cells(Element):
    def __init__(self, node, lnk):
        elements={'Cell': [Element.ELEMENT],}
        super(Cells, self).__init__(node, elements, lnk)


class Cell(Element):
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'ColSpan': [Element.INTEGER],
                 }
        super(Cell, self).__init__(node, elements, lnk)

