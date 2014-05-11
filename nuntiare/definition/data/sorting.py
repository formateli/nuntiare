# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from filter import get_groups
from ..element import Element
from ..enum import Enum
from ...tools import get_expression_value_or_default

class SortDirection(Enum):
    enum_list={'ascending': 'Ascending',
               'descending': 'Descending',  
              }
    def __init__(self, report, expression):
        super(SortDirection, self).__init__(report, 'SortDirection', expression, SortDirection.enum_list)


class Sorting(Element):
    def __init__(self, node, lnk):
        elements={'SortBy': [Element.ELEMENT],}
        self.sortby_list=[]
        super(Sorting, self).__init__(node, elements, lnk)


class SortBy(Element):
    def __init__(self, node, lnk):
        elements={'SortExpression': [Element.VARIANT],
                  'SortDirection': [Element.ENUM],
                 }
        super(SortBy, self).__init__(node, elements, lnk)
        lnk.parent.sortby_list.append(self)

        
class SortingObject(object):
    def __init__(self, sorting_def, test_sorting_list=None):
        self.sortby_list=[]
        if test_sorting_list: # We are unittest
            for srt in test_sorting_list:
                self.sortby_list.append(SortByObject(None, test_sortby=srt))
        else:
            for srt in sorting_def.sortby_list:
                self.sortby_list.append(SortByObject(srt))

    def sort_data(self, data):
        if len(self.sortby_list)==0:
            return

        groups=[]
        for sortby in self.sortby_list:
            direction = get_expression_value_or_default(None, None, "Ascending", 
                                            direct_expression=sortby.sort_direction)
            reverse = False if direction == "Ascending" else True
            groups = get_groups(data, sortby.sort_expression, groups)
            groups = sorted(groups, key=lambda z: z[0], reverse=reverse)

        if len (groups)==0:
            return
        data.rows=[]
        for g in groups:
            for r in g[1].rows:
                data.rows.append(r)
            del data.report.data_groups[g[1].name] # Delete from global collection


class SortByObject(object):
    def __init__(self, sortby_def, test_sortby=None):
        self.sort_expression=None
        self.sort_direction=None

        if test_sortby: # unitetst
            self.sort_expression = test_sortby[0]
            if len (test_sortby) > 1:
                self.sort_direction = test_sortby[1]
        else:
            if sortby_def:
                self.sort_expression = sortby_def.get_element("SortExpression")
                self.sort_direction = sortby_def.get_element("SortDirection")

