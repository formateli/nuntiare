# This file is part of Nuntiare project. 
# The COYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
import dateutil
from nuntiare.report import Report
from nuntiare.definition.expression import Expression
from nuntiare.definition.data.filter import FiltersObject
from nuntiare.definition.data.sorting import SortingObject
from nuntiare.definition.data.grouping import GroupingData, GroupingObject
from nuntiare.definition.data.data_source import DataSourceObject
from nuntiare.definition.data.data_set import DataSetObject, FieldsObject

class DataTest(unittest.TestCase):
    def testData(self):
        report = Report(string_xml="<Report><Name>Data Test</Name><Body></Body></Report>")
    
        f = open("db_test_connection_northwind", "r")
        conn_str = f.readline()
        f.close()

        ds = DataSourceObject()
        ds.connect(data_provider_name="postgresql", conn_string=conn_str)
    
        self.assertNotEqual(ds, None, "DataSource failed!")

        # In production, this list if obtained automatically from 'Fields' element of xml report file.
        field_list=[]   # [0] field_name used in Fields collections in a report, Ex Fields['id'] 
                        # [1] database field name,
                        # [2] Use with/out expressions 
        field_list.append(['id', 'orderid', None])
        field_list.append(['date', 'orderdate', None])                      
        field_list.append(['customer', 'customerid', None])
        field_list.append(['employee', 'employeeid', None])
        field_list.append(['freight', 'freight', None])
        field_list.append(['dummy', None, 'Dummy']) 
        field_list.append(['dummy_2', None, "='Dummy id ' + str(Fields['id'])"])# It can be an expression
        
        fields = FieldsObject(field_def=None, test_field_list=field_list)

        dataset = DataSetObject(name="date_test", 
                        report=report, 
                        cursor=ds.cursor, 
                        command_text="SELECT orderid, orderdate, customerid, employeeid, freight FROM orders ORDER BY orderid",
                        fields=fields)
        
        data = dataset.data # It is the DataInterface object
        self.assertEqual(len(data.rows), 830, "len(data.rows)")
        self.assertEqual(data.EOF(), True, "EOF for new Data")
        data.move_first() # Move to first row
        self.assertEqual(data.EOF(), False, "EOF at first row")
        i=10248
        while not data.EOF():
            self.assertEqual(data['id'], i, "id value")
            self.assertEqual(data['dummy'], 'Dummy', "dummy field value")
            self.assertEqual(data['dummy_2'], 'Dummy id ' + str(i), "dummy 2 field value")
            i=i+1
            data.move_next()
        self.assertEqual(data.EOF(), True, "EOF at the end of Data iteration")

        
        ##################### filter #####################
    
        filter_def=[]
        # Gets rows with id != 10248
        filter_def.append([Expression(report, "=Fields['id']"), 
                        Expression(report, "NotEqual"), 
                        [Expression(report,"=int(10248)"),]])        
        flt = FiltersObject(None, test_filter_list=filter_def)
        flt.filter_data(data)
        self.assertEqual(len(data.rows), 829, "len(data.rows)")
        
        filter_def=[]
        # Gets rows with ids between 10250 and 11076 (Remove frist and last row)
        filter_def.append([Expression(report, "=Fields['id']"), 
                        Expression(report, "Between"), 
                        [Expression(report,"=int(10250)"),Expression(report,"=int(11076)")]])        
        flt = FiltersObject(None, test_filter_list=filter_def)
        flt.filter_data(data)
        self.assertEqual(len(data.rows), 827, "len(data.rows)")
        
        
        ##################### sorting #####################
        
        sorting_def=[]
        # Sort by id 'Descending'
        sorting_def.append([Expression(report,"=Fields['id']"),
                        Expression(report,"Descending")])
        
        srt = SortingObject(None, test_sorting_list=sorting_def) 
        srt.sort_data(data)
        data.move_first()
        x=11076
        while not data.EOF():
            self.assertEqual(data['id'], x, "Sorted Descending")            
            data.move_next()
            x=x-1

        # Sort by id 'Ascending' by default
        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['id']"),])
        
        srt = SortingObject(None, test_sorting_list=sorting_def) 
        srt.sort_data(data)
        data.move_first()
        x=10250
        while not data.EOF():
            self.assertEqual(data['id'], x, "Sorted Ascending")
            data.move_next()
            x=x+1
        
        # Sort by customer 'Descending' and date 'Ascending'
        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['customer']"),Expression(report, "Descending")])        
        sorting_def.append([Expression(report,"=Fields['date']"),])

        srt = SortingObject(None, test_sorting_list=sorting_def) 
        srt.sort_data(data)    

        data.move_first()
        self.assertEqual(data['customer'], 'VICTE', "Sorting. customer at first row")
        self.assertEqual(data['date'], dateutil.parser.parse('1996-07-08').date() , "Sorting. date at first row")                
        data.move(100)
        self.assertEqual(data['customer'], 'LAMAI', "Sorting. customer at row 100")
        self.assertEqual(data['date'], dateutil.parser.parse('1996-11-11').date() , "Sorting. date at row 100")                        
        data.move_last()
        self.assertEqual(data['customer'], 'BONAP', "Sorting. customer at last row")
        self.assertEqual(data['date'], dateutil.parser.parse('1998-05-06').date() , "Sorting. date at last row")                        

#        data.move_first()        
#        while not data.EOF():
#            print str(data['customer']) +  " - " + str(data['date'])
#            data.move_next()        
        
        ##################### grouping #####################
        
        grp = GroupingData(data) # Initial data
        self.assertEqual(grp.has_groups(), False, "grp has_groups = False")        
                
        
        ########## group by customer
        
        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['customer']"),
                        Expression(report,"Descending")])        
        grouping_def=[Expression(report,"customer"), None, None, None, None, 
                        [Expression(report, "=Fields['customer']"), ]]
                        
        group_customer = GroupingObject(None, test_grouping_list=grouping_def)
                
        grp.grouping_by(group_customer, None, 
                        test_sorting_list=sorting_def)
        self.assertEqual(grp.has_groups(), True, "grp has_groups = True")
        
        group_list=grp.get_group("customer")
        self.assertEqual(len(group_list), 89, "group customer: len(group_list) = 89")

#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
            
#        return

        ########## group by employee

        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['employee']"),
                        Expression(report,"Ascending")])
        grouping_def=[Expression(report,"employee"), None, None, None, None, 
                        [Expression(report, "=Fields['employee']"), ]]
        group_employee = GroupingObject(None, test_grouping_list=grouping_def)
        
        grp.grouping_by(group_employee, None, 
                        test_sorting_list=sorting_def)

        self.assertEqual(grp.has_groups(), True, "grp has_groups = True")
        
        group_list=grp.get_group("employee")
#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
        self.assertEqual(len(group_list), 463, "group employee: len(group_list) = 463")

        
        ################# group by date

        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['date']"),
                        Expression(report,"Descending")])
        grouping_def=[Expression(report,"date"), None, None, None, None, 
                        [Expression(report, "=Fields['date']"), ]]
        group_date = GroupingObject(None, test_grouping_list=grouping_def)
        
        grp.grouping_by(group_date, None, 
                        test_sorting_list=sorting_def)

        self.assertEqual(grp.has_groups(), True, "grp has_groups = True")
        
        group_list=grp.get_group("date")
#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
        self.assertEqual(len(group_list), 827, "group date: len(group_list) = 827")                        

