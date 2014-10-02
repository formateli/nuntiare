# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data_region import DataRegion
from .... types.element import Element
from ..... tools import raise_error_with_log

class Tablix(DataRegion):
    def __init__(self, node, lnk):
        elements={'TablixCorner': [Element.ELEMENT],
                  'TablixBody': [Element.ELEMENT],
                  'TablixColumnHierarchy': [Element.ELEMENT],
                  'TablixRowHierarchy': [Element.ELEMENT],
                  'LayoutDirection': [Element.ENUM],
                  'GroupsBeforeRowHeaders': [Element.INTEGER, True],
                  'RepeatColumnHeaders': [Element.BOOLEAN, True],
                  'RepeatRowHeaders': [Element.BOOLEAN, True],
                  'FixedColumnHeaders': [Element.BOOLEAN, True],
                  'FixedRowHeaders': [Element.BOOLEAN, True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN, True],
                  'KeepTogether': [Element.BOOLEAN, True],
                 }
        super(Tablix, self).__init__('Tablix', node, lnk, elements)       
        
        self.verify_required(["TablixColumnHierarchy","TablixMembers"])
        self.verify_required(["TablixRowHierarchy","TablixMembers"])
        self.verify_required(["TablixBody","TablixColumns"])
        self.verify_required(["TablixBody","TablixRows"])
        
    def verify_required(self, elements=[]):
        el=None
        str_error = None
        for e in elements:
            if not el:
                el = self.get_element(e)
                str_error = "'" + e + "'"
            else:
                el = el.get_element(e)
                str_error = str_error + "-->'" + e + "'"
            if not el:
                break
        if not el:
            raise_error_with_log("{0} element is required in Tablix: '{1}'.".format(str_error, self.name))


class TablixCorner(Element):
    '''
    The TablixCorner element defines the layout and structure of the 
    upper left-hand corner region of a Tablix
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerRows': [Element.ELEMENT],}
        super(TablixCorner, self).__init__(node, elements, lnk)


class TablixCornerRows(Element):
    '''
    The TablixCornerRows element defines the list of rows in the TablixCorner.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerRow': [Element.ELEMENT],}
        super(TablixCornerRows, self).__init__(node, elements, lnk)        


class TablixCornerRow(Element):
    '''
    The TablixCornerRow element defines the list of cells in a row 
    of the corner section of a Tablix. The height of the row is equal to 
    the height of the corresponding column TablixHeader
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCornerCell': [Element.ELEMENT],}
        super(TablixCornerRow, self).__init__(node, elements, lnk)  


class TablixCornerCell(Element):
    '''
    The TablixCornerCell element defines the contents of each 
    corner cell in the Tablix. The width of the each column is equal 
    to the width of the corresponding row TablixHeader.
    '''
    
    def __init__(self, node, lnk):
        elements={'CellContents': [Element.ELEMENT],}
        super(TablixCornerCell, self).__init__(node, elements, lnk)  


class CellContents(Element):
    '''
    The CellContents element defines the report item contained in a body, 
    header or corner cell of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'ReportItems': [Element.ELEMENT],
                  'ColSpan': [Element.INTEGER, True],
                  'RowSpan': [Element.INTEGER, True],
                 }
        super(CellContents, self).__init__(node, elements, lnk) 


class TablixHierarchy(Element):
    '''
    The virtual TablixHierarchy element defines a hierarchy of members for the tablix
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixMembers': [Element.ELEMENT],}
        super(TablixHierarchy, self).__init__(node, elements, lnk)


class TablixRowHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixRowHierarchy, self).__init__(node, lnk)


class TablixColumnHierarchy(TablixHierarchy):
    def __init__(self, node, lnk):
        super(TablixColumnHierarchy, self).__init__(node, lnk)        


class TablixMembers(Element):
    '''
    The TablixMembers element defines a list of members in a Tablix hierarchy.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixMember': [Element.ELEMENT],}
        self.member_list=[]
        super(TablixMembers, self).__init__(node, elements, lnk)


class TablixMember(Element):
    '''
    The TablixMember element defines a member of a tablix hierarchy.
    '''
    
    def __init__(self, node, lnk):
        elements={'Group': [Element.ELEMENT],
                  'SortExpressions': [Element.ELEMENT],
                  'TablixHeader': [Element.ELEMENT],
                  'TablixMembers': [Element.ELEMENT],
                  'FixedData': [Element.BOOLEAN, True],
                  'Visibility': [Element.ELEMENT],
                  'HideIfNoRows': [Element.BOOLEAN, True],
                  'KeepWithGroup': [Element.ENUM],
                  'RepeatOnNewPage': [Element.BOOLEAN, True],
                  'DataElementName': [Element.STRING, True],
                  'DataElementOutput': [Element.ENUM],
                  'KeepTogether': [Element.BOOLEAN, True],                                                         
                 }
        super(TablixMember, self).__init__(node, elements, lnk)
        lnk.parent.member_list.append(self)


class TablixHeader(Element):
    '''
    The TablixHeader element defines the ReportItem to use as the header for the group.
    '''
    
    def __init__(self, node, lnk):
        elements={'Size': [Element.SIZE],
                  'CellContents': [Element.ELEMENT],
                 }
        super(TablixHeader, self).__init__(node, elements, lnk)  


class TablixBody(Element):
    '''
    The TablixBody element defines the layout and structure of the 
    bottom right region that contains the data elements of the Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixColumns': [Element.ELEMENT],
                  'TablixRows': [Element.ELEMENT],
                 }
        super(TablixBody, self).__init__(node, elements, lnk)
        

class TablixColumns(Element):
    '''
    The TablixColumns element defines the set of columns 
    in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixColumn': [Element.ELEMENT],}
        self.column_list=[]
        super(TablixColumns, self).__init__(node, elements, lnk)
        
        
class TablixColumn(Element):
    '''
    The TablixColumn element defines a column in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'Width': [Element.SIZE],}
        super(TablixColumn, self).__init__(node, elements, lnk)
        lnk.parent.column_list.append(self)


class TablixRows(Element):
    '''
    The TablixRows element defines the list of rows in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixRow': [Element.ELEMENT],}
        self.row_list=[]
        super(TablixRows, self).__init__(node, elements, lnk)


class TablixRow(Element):
    '''
    The TablixRow element defines a list of cells in a row of the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'Height': [Element.SIZE],
                  'TablixCells': [Element.ELEMENT],
                 }
        super(TablixRow, self).__init__(node, elements, lnk)
        lnk.parent.row_list.append(self)
    

class TablixCells(Element):
    '''
    The TablixCells element defines the list of cells in 
    a row of the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'TablixCell': [Element.ELEMENT],}
        super(TablixCells, self).__init__(node, elements, lnk)


class TablixCell(Element):
    '''
    The TablixCell element defines the contents of each cell 
    in the body section of a Tablix.
    '''
    
    def __init__(self, node, lnk):
        elements={'CellContents': [Element.ELEMENT],
                  'DataElementName': [Element.STRING, True],
                  'DataElementOutput': [Element.ENUM],
                 }
        super(TablixCell, self).__init__(node, elements, lnk)

