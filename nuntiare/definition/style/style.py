# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.definition.element import Element

class Style(Element):
    '''
    The Style element contains information about 
    the style of a report item. Where possible, the style
    property names and values match standard HTML/CSS properties.
    '''

    def __init__(self, node, lnk):
        elements={'BorderColor': [Element.ELEMENT], 
                  'BorderStyle': [Element.ELEMENT],
                  'BorderWidth': [Element.ELEMENT],
                  'BackgroundColor': [Element.COLOR],
                  'BackgroundGradientType': [Element.ENUM, 'BackgroundGradientType'],
                  'BackgroundGradientEndColor': [Element.COLOR],
                  'BackgroundImage': [Element.ELEMENT],
                  'FontStyle': [Element.ENUM, 'FontStyle'],
                  'FontFamily': [Element.STRING],
                  'FontSize': [Element.SIZE],
                  'FontWeight': [Element.ENUM, 'FontWeight'],
                  'Format': [Element.STRING],
                  'TextDecoration': [Element.ENUM, 'TextDecoration'],
                  'TextAlign': [Element.ENUM, 'TextAlign'],
                  'VerticalAlign': [Element.ENUM, 'VerticalAlign'],
                  'Color': [Element.COLOR],
                  'PaddingLeft': [Element.SIZE],
                  'PaddingRight': [Element.SIZE],
                  'PaddingTop': [Element.SIZE],
                  'PaddingBottom': [Element.SIZE],
                  'LineHeight': [Element.SIZE],
                  'Direction': [Element.ENUM, 'TextDirection'],
                  'WritingMode': [Element.ENUM, 'WritingMode'],
                 }

        super(Style, self).__init__(node, elements, lnk)



