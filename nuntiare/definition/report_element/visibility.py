# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from .. types.element import Element

class Visibility(Element):
    '''
    The Visibility element indicates if the ReportItem should be shown in the rendered report. If no
    Visibility element is present, the item is unconditionally shown.
    '''

    def __init__(self, node, lnk):
        elements={'Hidden': [Element.BOOLEAN],
                  'ToggleItem': [Element.STRING, True],
                 }
        super(Visibility, self).__init__(node, elements, lnk)

