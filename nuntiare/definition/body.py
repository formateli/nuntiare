# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from element import Element

class Body(Element):
    def __init__(self, node, lnk):
        elements={'Height': [Element.SIZE], 
                  'Style': [Element.ELEMENT],
                  'ReportItems': [Element.ELEMENT],
                  'Columns': [Element.INTEGER],
                  'ColumnSpacing': [Element.SIZE],
                 }
        super(Body, self).__init__(node, elements, lnk)

