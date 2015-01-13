# This file is part of Nuntiare project. 
# The COYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
import dateutil
from nuntiare.definition.report_def import ReportDef
from nuntiare.report.report import Report

class DataTest(unittest.TestCase):
    def testData(self):
        report_def = ReportDef(string_xml = self.get_xml_string())        
        report = Report(report_def)
    
        f = open("db_test_connection_northwind", "r")
        conn_str = f.readline()
        f.close()
        
        parameters={'conn_string':conn_str}
        report.run(parameters)

        self.assertNotEqual(report.data_sources['DataSourceTest'], 
                            None, "DataSource failed!")
        self.assertEqual(report.data_sources['DataSourceTest'].data_source_def.name, 
                            'DataSourceTest', "DataSource name")

        # DataSet without filter
        data = report.data_sets['DataSet1'].data # It is the DataInterface object
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


        # DataSet filtered
        data = report.data_sets['DataSetFiltered'].data
        self.assertEqual(len(data.rows), 827, "len(data.rows)")
        data.move_first()
        i=10248
        while not data.EOF():
            if i in (10248, 10249, 11077):
                self.assertNotEqual(data['id'], i, "id value")
                i=i+1
                continue
            self.assertEqual(data['id'], i, "id value")
            self.assertEqual(data['dummy2'], 'Dummy', "dummy field value")
            self.assertEqual(data['dummy_22'], 'Dummy id ' + str(i), "dummy 2 field value")
            i=i+1
            data.move_next()

        
        # Sort by id 'Descending'
        data = report.data_sets['DataSetSort1'].data
        data.move_first()
        x=11077
        while not data.EOF():
            self.assertEqual(data['id'], x, 
                    "Sorted Descending. Must be '{0}' but was '{1}': ".format(x, data['id']))
            data.move_next()
            x=x-1
            
            
        # Sort by customer 'Descending' and date 'Ascending'
        data = report.data_sets['DataSetSort2'].data
        self.assertEqual(len(data.rows), 830, "Sorting. len(data.rows")

        data.move_first()
        self.assertEqual(data['customer'], 'WOLZA', 
                        "Sorting. Must be '{0}' but was '{1}'".format('WOLZA', data['customer']))
        self.assertEqual(data['date'], dateutil.parser.parse('1996-12-05').date() , "Sorting. date at first row")

        data.move(100)
        self.assertEqual(data['customer'], 'TORTU', 
                        "customer at row 100. Must be '{0}' but was '{1}'".format('TORTU', data['customer']))        
        self.assertEqual(dateutil.parser.parse(str(data['date'])), dateutil.parser.parse('1996-10-02'), 
                        "date at row 100. Must be '{0}' but was '{1}'".format(dateutil.parser.parse('19961002').date(), data['date']))
        data.move_last()
        self.assertEqual(data['customer'], 'ALFKI', "Sorting. customer at last row")
        self.assertEqual(data['date'], dateutil.parser.parse('1998-04-09').date() , "Sorting. date at last row")


        # DataRegion group
#        data = report.data_groups['Tablix1'].data
#        data.move_first()
        #x=11077
        #while not data.EOF():
        #    self.assertEqual(data['id'], x, 
        #            "Sorted Descending. Must be '{0}' but was '{1}': ".format(x, data['id']))
        #    data.move_next()
        #    x=x-1

        return
        
        
        
        
        
        ##################### grouping #####################
        
        grp = GroupingData(data) # Initial data
        
        ########## group by customer
        
        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['customer']", False),
                        Expression(report,"Descending", False)])
        grouping_def=[Expression(report,"customer", False), None, None, None, None, 
                        [Expression(report, "=Fields['customer']", False), ]]
                        
        group_customer = GroupingObject(None, test_grouping_list=grouping_def)
                
        grp.grouping_by(group_customer, None, 
                        test_sorting_list=sorting_def)
        
        group_list=grp.get_group("customer")
        self.assertEqual(len(group_list), 89, "group customer: len(group_list) = 89")

#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
            
#        return


        ########## group by employee

        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['employee']", False),
                        Expression(report,"Ascending", False)])
        grouping_def=[Expression(report,"employee", False), None, None, None, None, 
                        [Expression(report, "=Fields['employee']", False), ]]
        group_employee = GroupingObject(None, test_grouping_list=grouping_def)
        
        grp.grouping_by(group_employee, None, 
                        test_sorting_list=sorting_def)

        
        group_list=grp.get_group("employee")
#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
        self.assertEqual(len(group_list), 463, "group employee: len(group_list) = 463")

        
        ################# group by date

        sorting_def=[]
        sorting_def.append([Expression(report,"=Fields['date']", False),
                        Expression(report,"Descending", False)])
        grouping_def=[Expression(report,"date", False), None, None, None, None, 
                        [Expression(report, "=Fields['date']", False), ]]
        group_date = GroupingObject(None, test_grouping_list=grouping_def)
        
        grp.grouping_by(group_date, None, 
                        test_sorting_list=sorting_def)
        
        group_list=grp.get_group("date")
#        print "\nlen(group_list): " + str(len(group_list))
#        for g in group_list:
#            print " " + g.name
        self.assertEqual(len(group_list), 827, "group date: len(group_list) = 827")                        

    def get_xml_string(self):
        return '''
            <Nuntiare>
                <Name>Data Test</Name>
                <Width>21cm</Width>
                <Page></Page>
                <DataSources>
                    <DataSource>
                        <Name>DataSourceTest</Name>
                        <ConnectionProperties>
                            <DataProvider>postgresql</DataProvider>
                            <ConnectString>=Parameters['conn_string']</ConnectString>
                        </ConnectionProperties>
                    </DataSource>
                </DataSources>                
                <DataSets>
                    <DataSet>
                        <Name>DataSet1</Name>
                        <Fields>
                            <Field>
                                <Name>id</Name>
                                <DataField>orderid</DataField>
                            </Field>
                            <Field>
                                <Name>date</Name>
                                <DataField>orderdate</DataField>
                            </Field> 
                            <Field>
                                <Name>customer</Name>
                                <DataField>customerid</DataField>
                            </Field> 
                            <Field>
                                <Name>employee</Name>
                                <DataField>employeeid</DataField>
                            </Field> 
                            <Field>
                                <Name>freight</Name>
                                <DataField>freight</DataField>
                            </Field>
                            <Field>
                                <Name>dummy</Name>
                                <Value>Dummy</Value>
                            </Field>
                            <Field>
                                <Name>dummy_2</Name>
                                <Value>='Dummy id ' + str(Fields['id'])</Value>
                            </Field>
                        </Fields>
                        
                        <Query>
                            <DataSourceName>DataSourceTest</DataSourceName>
                            <CommandText>SELECT orderid, orderdate, customerid, employeeid, freight FROM orders ORDER BY orderid</CommandText>
                        </Query>

                    </DataSet>

                    <DataSet>
                        <Name>DataSetFiltered</Name>
                        <Fields>
                            <Field>
                                <Name>id</Name>
                                <DataField>orderid</DataField>
                            </Field>
                            <Field>
                                <Name>date2</Name>
                                <DataField>orderdate</DataField>
                            </Field> 
                            <Field>
                                <Name>customer2</Name>
                                <DataField>customerid</DataField>
                            </Field> 
                            <Field>
                                <Name>employee2</Name>
                                <DataField>employeeid</DataField>
                            </Field> 
                            <Field>
                                <Name>freight2</Name>
                                <DataField>freight</DataField>
                            </Field>
                            <Field>
                                <Name>dummy2</Name>
                                <Value>Dummy</Value>
                            </Field>
                            <Field>
                                <Name>dummy_22</Name>
                                <Value>='Dummy id ' + str(Fields['id'])</Value>
                            </Field>
                        </Fields>
                        
                        <Query>
                            <DataSourceName>DataSourceTest</DataSourceName>
                            <CommandText>SELECT orderid, orderdate, customerid, employeeid, freight FROM orders ORDER BY orderid</CommandText>
                        </Query>
                        
                        <Filters>
                            <Filter>
                                <FilterExpression>=Fields['id']</FilterExpression>
                                <Operator>NotEqual</Operator>
                                <FilterValues>
                                    <FilterValue>=int(10248)</FilterValue>
                                </FilterValues>
                            </Filter>
                            <Filter>
                                <FilterExpression>=Fields['id']</FilterExpression>
                                <Operator>Between</Operator>
                                <FilterValues>
                                    <FilterValue>=int(10250)</FilterValue>
                                    <FilterValue>=int(11076)</FilterValue>                                    
                                </FilterValues>
                            </Filter>                            
                        </Filters>
                    </DataSet>

                    <DataSet>
                        <Name>DataSetSort1</Name>
                        <Fields>
                            <Field>
                                <Name>id</Name>
                                <DataField>orderid</DataField>
                            </Field>
                            <Field>
                                <Name>date</Name>
                                <DataField>orderdate</DataField>
                            </Field> 
                        </Fields>
                        
                        <Query>
                            <DataSourceName>DataSourceTest</DataSourceName>
                            <CommandText>SELECT orderid, orderdate FROM orders ORDER BY orderid</CommandText>
                        </Query>
                        
                        <SortExpressions>
                            <SortExpression>
                                <Value>=Fields['id']</Value>
                                <SortDirection>Descending</SortDirection>
                            </SortExpression>
                        </SortExpressions>
                        
                    </DataSet>

                    <DataSet>
                        <Name>DataSetSort2</Name>
                        <Fields>
                            <Field>
                                <Name>id</Name>
                                <DataField>orderid</DataField>
                            </Field>
                            <Field>
                                <Name>date</Name>
                                <DataField>orderdate</DataField>
                            </Field> 
                            <Field>
                                <Name>customer</Name>
                                <DataField>customerid</DataField>
                            </Field>                             
                        </Fields>
                        
                        <Query>
                            <DataSourceName>DataSourceTest</DataSourceName>
                            <CommandText>SELECT orderid, orderdate, customerid FROM orders ORDER BY orderid</CommandText>
                        </Query>
                        
                        <SortExpressions>                        
                            <SortExpression>
                                <Value>=Fields['customer']</Value>
                                <SortDirection>Descending</SortDirection>
                            </SortExpression>
                            <SortExpression>
                                <Value>=Fields['date']</Value>
                           </SortExpression>
                        </SortExpressions>
                    </DataSet>
                </DataSets>
                
                <ReportParameters>
                    <ReportParameter>
                        <Name>conn_string</Name>
                        <DataType>String</DataType>
                        <DefaultValue>''</DefaultValue>
                    </ReportParameter>
                </ReportParameters>

                <Body>
                    <Height>300in</Height>
                    <ReportItems>
                        <Tablix>
                            <Name>Tablix1</Name>
                            <DataSetName>DataSet1</DataSetName>                        
                            <TablixColumnHierarchy>
                                <TablixMembers>
                                    <TablixMember />
                                </TablixMembers>
                            </TablixColumnHierarchy>                        
                            <TablixRowHierarchy>
                                <TablixMembers>
                                    <TablixMember>
                                        <Group>
                                            <Name>Details</Name>
                                        </Group>
                                    </TablixMember>
                                </TablixMembers>
                            </TablixRowHierarchy> 
                            
                            <TablixBody>
                                <TablixColumns>
                                    <TablixColumn>
                                        <Width>5.5in</Width>
                                    </TablixColumn>
                                </TablixColumns>                        
     
                                <TablixRows>
                                    <TablixRow>
                                        <Height>0.42in</Height>
                                        <TablixCells>
                                            <TablixCell>
                                                <CellContents>
                                                    <Rectangle Name="Rectangle1">
                                                        <ReportItems />
                                                    </Rectangle>
                                                </CellContents>
                                            </TablixCell>
                                        </TablixCells>
                                    </TablixRow>
                                </TablixRows>
                            </TablixBody>
                        </Tablix> 
                     </ReportItems>               
                </Body>
            </Nuntiare>
            '''
 
