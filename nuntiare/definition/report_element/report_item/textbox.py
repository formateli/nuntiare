# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from report_item import ReportItem
from ... types.element import Element
from .... tools import get_expression_value_or_default

class Textbox(ReportItem):
    def __init__(self, node, lnk):
        elements={'Value': [Element.VARIANT],
                  'CanGrow': [Element.BOOLEAN, True],
                  'CanShrink': [Element.BOOLEAN, True],
                  'HideDuplicates': [Element.STRING, True],
                  'ToggleImage': [Element.ELEMENT],
                  'DataElementStyle': [Element.ENUM],                  
                 }
        super(Textbox, self).__init__("Textbox", node, lnk, elements)
        self.can_grow = get_expression_value_or_default (None, self, "CanGrow", False)
        self.can_shrink = get_expression_value_or_default (None, self, "CanShrink", False)
        self.hide_duplicates = get_expression_value_or_default (None, self, "HideDuplicates", None)
        
        
class ToggleImage(Element):
    '''
    Indicates the initial state of a toggle image should such an image be displayed as a part of the
    text box. The image is always displayed if the text box is a toggle item for another report item.
    Whenever the text box/image is clicked on, the toggle image state flips and the image associated
    with the new state is displayed instead
    InitialState:
        A Boolean expression, the value of which determines the
        initial state of the toggle image. True = 'expanded' (that
        is, a minus sign). False = 'collapsed' (that is, a plus sign).    
    '''

    def __init__(self, node, lnk):
        elements={'InitialState': [Element.BOOLEAN],}
        super(ToggleImage, self).__init__(node, elements, lnk)

