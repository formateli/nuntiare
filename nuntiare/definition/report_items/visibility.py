# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. element import Element

class Visibility(Element):
    def __init__(self, node, lnk):
        elements={'Hidden': [Element.BOOLEAN],
                  'ToggleItem': [Element.STRING],
                 }
        super(Visibility, self).__init__(node, elements, lnk)

