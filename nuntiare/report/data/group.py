# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.


class GroupingObject(object):
    def __init__(self, group_def):
        self.expression_list=[]
        self.name=None
        self.page_break=None
        self.filters=None
        self.parent=None
        
        if group_def:
            self.name = group_def.get_element("Name")            
            self.page_break_at_start = group_def.get_element("PageBreakAtStart")
            self.page_break_at_end = group_def.get_element("PageBreakAtEnd")
            self.filters = group_def.get_element("Filters")
            self.parent = group_def.get_element("Parent")
            exps = group_def.get_element("GroupExpressions")
            for ex in exps.expression_list:
                self.expression_list.append(ex)
        
