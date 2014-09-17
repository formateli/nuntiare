# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from ..types.element import Element

class BreakLocation(Enum):
    '''
    Indicates where the page break should occur.
    Start:
        There should be a page break before the report item or each
        instance of the group.
    End:
        There should be a page break    after the report item or each
        instance of the group.
    StartAndEnd:
        There should be a page break both before and after the
        report item or each instance of the group.
    Between
        There should be a page break between each instance of the
        group (does not apply to report items).    
    '''
    
    enum_list={'start': 'Start',
               'end': 'End', 
               'startandend': 'StartAndEnd', 
               'center': 'Center', 
               'between': 'Between', 
              }

    def __init__(self, expression):
        super(BreakLocation, self).__init__('BreakLocation', expression, BreakLocation.enum_list)


class PageBreak(Element):
    '''
    The PageBreak element defines page break behavior for a group or report item.
    '''

    def __init__(self, node, lnk):
        elements={'BreakLocation': [Element.ENUM],}
        super(PageBreak, self).__init__(node, elements, lnk)
        
