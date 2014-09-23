# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from data import get_groups
from ... tools import get_expression_value_or_default

class SortingObject(object):
    def __init__(self, report, sorting_def):
        self.report = report
        self.sortby_list=[]
        for srt in sorting_def.sortby_list:
            self.sortby_list.append(SortByObject(srt))

    def sort_data(self, data):
        if len(self.sortby_list)==0:
            return

        groups=[]
        i=0
        for sortby in self.sortby_list:
            direction = get_expression_value_or_default(self.report, None, None, "Ascending", 
                                            direct_expression=sortby.sort_direction)
            reverse = False if direction == "Ascending" else True
            if i==0:    
                groups = get_groups(data, sortby.sort_value, sub_groups=[])
                groups = sorted(groups, key=lambda z: z[0], reverse=reverse)
            else:
                #Sort is made in get_groups function.
                groups = get_groups(data, sortby.sort_value, sub_groups=groups, sort_descending=reverse)
            i=i+1 
        
        if len (groups)==0:
            return
        data.rows=[]
        for g in groups:
            for r in g[1].rows:
                data.rows.append(r)
            del data.report.data_groups[g[1].name] # Delete from global collection


class SortByObject(object):
    def __init__(self, sortby_def):
        self.sort_expression=None
        self.sort_direction=None

        if sortby_def:
            self.sort_value = sortby_def.get_element("Value")
            self.sort_direction = sortby_def.get_element("Direction")
