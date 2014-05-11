# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data import DataGroup
from sorting import SortingObject
from filter import FiltersObject
from ..element import Element
from ..expression_list import ExpressionList
from ...tools import get_expression_value_or_default

class Grouping(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'GroupExpressions': [Element.EXPRESSION_LIST],
                  'PageBreakAtStart': [Element.BOOLEAN],
                  'PageBreakAtEnd': [Element.BOOLEAN],
                  'Filters': [Element.ELEMENT],
                  'Parent': [Element.VARIANT],
                 }
        super(Grouping, self).__init__(node, elements, lnk)


class GroupExpressions(ExpressionList):
    def __init__(self, node, lnk):
        elements={'GroupExpression': [Element.VARIANT],}
        super(GroupExpressions, self).__init__(node, elements, lnk)
        

class GroupingData(object):
    def __init__(self, data):
        self.data = data
        self.group_data=None
        self.groups={} # key: grouping name, value: list of groups that for this grouping
        self.last_group_name=None
    
    def has_groups(self):
        if self.group_data:
            return True
        return False
    
    def grouping_by(self, grouping_object, sorting_def, optional_name=None, test_sorting_list=None):       
        if optional_name:
            name = optional_name
        else:
            name = get_expression_value_or_default(None,None,None, direct_expression=grouping_object.name)

        break_at_start = get_expression_value_or_default(None,None,False, direct_expression=grouping_object.page_break_at_start)
        break_at_end = get_expression_value_or_default(None,None,False, direct_expression=grouping_object.page_break_at_end)
        
        self.groups[name] = []
        if not self.group_data:
            self.group_data = DataGroup(self.data, name, break_at_start, break_at_end)
            self.group_data.add_rows_by_parent()
            self.filter(self.group_data, grouping_object.filters)
            self.sort(self.group_data, sorting_def, test_sorting_list=test_sorting_list)
            # Group
            self.group_data.create_groups(grouping_object.expression_list, break_at_start, break_at_end)            
            for g in self.group_data.groups:         
                self.groups[name].append(g)
        else:
            group_list = self.get_group(self.last_group_name)
            for g in group_list:
                g.create_groups(grouping_object.expression_list, break_at_start, break_at_end)
                for g2 in g.groups:
                    self.filter(g2, grouping_object.filters)                    
                    self.sort(g2, sorting_def, test_sorting_list=test_sorting_list)                
                    self.groups[name].append(g2)
                    
        self.last_group_name = name
                
    def get_group(self, name):
        result = []
        if self.groups.has_key(name):
            result = self.groups[name]
        return result

    def filter(self, data, filters):
        if filters:
            flt = FiltersObject(filters)
            flt.filter_data(data)
            
    def sort(self, data, sorting_def, test_sorting_list=None):
        if test_sorting_list: # unittest
            srt = SortingObject(None, test_sorting_list=test_sorting_list)
            srt.sort_data(data)
        else:
            if sorting_def:
                srt = SortingObject(sorting_def)
                srt.sort_data(data)                


class GroupingObject(object):
    def __init__(self, grouping_def, test_grouping_list=None):
        self.expression_list=[]
        self.name=None
        self.page_break_at_start=None
        self.page_break_at_end=None
        self.filters=None
        self.parent=None
        
        if test_grouping_list: # unittest
            self.name = test_grouping_list[0]
            self.page_break_at_start = test_grouping_list[1]
            self.page_break_at_end = test_grouping_list[2]
            self.filters = test_grouping_list[3]
            self.parent = test_grouping_list[4]
            for ex in test_grouping_list[5]:
                self.expression_list.append(ex)
        else:
            if grouping_def:
                self.name = grouping_def.get_element("Name")            
                self.page_break_at_start = grouping_def.get_element("PageBreakAtStart")
                self.page_break_at_end = grouping_def.get_element("PageBreakAtEnd")
                self.filters = grouping_def.get_element("Filters")
                self.parent = grouping_def.get_element("Parent")
                exps = grouping_def.get_element("GroupExpressions")
                for ex in exps.expression_list:
                    self.expression_list.append(ex)
                    
