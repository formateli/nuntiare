# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class ReportItemGroup(object):
    def __init__(self, name, report):
        self.items={}
        self.name = name
        self.report = report

    def __getitem__(self, key):
        if not key in self.items:
            raise KeyError("Textbox '{0}' not found in ReportItems collection '{1}'".format(key, self.name))
 
        # In a report iteration, ReportItems['name'] always returns last object value
        # in the current scope
        return self.items[key][len(self.items[key]) - 1].value
        
    #TODO Remove, use Variable
    def sum(self, *args):
        #print "Looking in '{0}'".format(self.name)
        total = 0        
        for f in args:
            str_error= "'sum' Error. Textbox '{0}' not found in group '{1}'".format(f, self.name)
            if not f in self.items:
                # Verify if it is a parent group of a data grouping.
                if self.name in self.report.data_groups:
                    if len(self.report.data_groups[self.name].groups)==0:
                        raise KeyError(str_error)
                    for grp in self.report.data_groups[self.name].groups:
                        # We use ReportItems groups
                        if not grp.name in self.report.report_items_group:
                            raise KeyError(str_error)
                        total = total + self.report.report_items_group[grp.name].sum(f)
                else:
                    raise KeyError(str_error)
            else:
                for v in self.items[f]:
                    total = total + v.value
        return total
        
    def add_item(self, name, item):
        if not name in self.items:
            self.items[name]=[]
        self.items[name].append(item) 

