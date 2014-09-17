# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from types.element import Element

class ActionInfo(Element):
    '''
    The ActionInfo element defines a list of actions and action 
    style associated with a ReportItem.
    '''

    def __init__(self, node, lnk):
        elements={'Actions': [Element.ELEMENT],}
        super(ActionInfo, self).__init__(node, elements, lnk)        


class Actions(Element):
    '''
    The Actions element defines a list of actions associated with a ReportItem.
    '''

    def __init__(self, node, lnk):
        elements={'Action': [Element.ELEMENT],}
        super(Actions, self).__init__(node, elements, lnk)   


class Action(Element):
    '''
    The Action element defines a hyperlink, bookmark link or drillthrough 
    action associated with a ReportItem.
    '''

    def __init__(self, node, lnk):
        elements={'Hyperlink': [Element.URL],
                  'Drillthrough': [Element.ELEMENT],
                  'BookmarkLink': [Element.STRING],
                 }
        super(Action, self).__init__(node, elements, lnk)   
        
        
class Drillthrough(Element):
    def __init__(self, node, lnk):
        elements={'ReportName': [Element.STRING],
                  'Parameters': [Element.ELEMENT],
                 }
        super(Drillthrough, self).__init__(node, elements, lnk)          
        
