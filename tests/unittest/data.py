# This file is part of Nuntiare project.
# The COYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import unittest
import os
import dateutil
from nuntiare.report import Report
from tools import get_test_path


class DataTest(unittest.TestCase):
    def test_data(self):
        report1 = Report(self._get_xml_string_1())

        with open(get_test_path(
                'db_test_connection_northwind'), 'r') as con_file_info:
            conn_str = con_file_info.readline()

        parameters = {'conn_string': conn_str}
        report1.run(parameters)
        self._verify(report1)

        # Save DataSets without filtering and sortening in
        # a new file with .nuntiare extension
        report1.save(True)

        f_result = os.path.join(
            report1.globals['OutputDirectory'],
            report1.globals['OutputName'] + '.nuntiare')

        # Same result as Above, because
        # Database emmbeded is not used.
        report2 = Report(f_result)
        report2.run(parameters)
        self._verify(report2)

        # Load data stored in file
        report2.run()  # --> No parameters
        self._verify(report2)

    def test_sortening(self):
        report = Report(self._get_xml_string_2())

        with open(get_test_path(
                'db_test_connection_adventure'), 'r') as con_file_info:
            conn_str = con_file_info.readline()

        parameters = {'conn_string': conn_str}
        report.run(parameters)

        country_group = report.data_groups["Country"]
        self.assertEqual(len(country_group.instances), 6)
        i = 0
        country_group.move_first()
        while not country_group.EOF:
            data1 = country_group.current_instance().data
            data2 = country_group.instances[i].data
            self.assertEqual(data1, data2)
            data3 = country_group.current_instance().sub_instance[0].data
            if i == 0:
                self.assertEqual(data1.fields.CountryRegion, "Australia")
                self._check_sorting_instance_data(data3, [
                        ['Australia', 'Alexandria'],
                        ['Australia', 'Sydney']
                    ])
            elif i == 1:
                self.assertEqual(data1.fields.CountryRegion, "Canada")
                self._check_sorting_instance_data(data3, [
                        ['Canada', 'Barrie'],
                        ['Canada', 'Winnipeg']
                    ])
            elif i == 2:
                self.assertEqual(data1.fields.CountryRegion, "France")
                self._check_sorting_instance_data(data3, [
                        ['France', 'Bordeaux'],
                        ['France', 'Bordeaux']
                    ])
            elif i == 3:
                self.assertEqual(data1.fields.CountryRegion, "Germany")
                self._check_sorting_instance_data(data3, [
                        ['Germany', 'Berlin'],
                        ['Germany', 'Berlin']
                    ])
            elif i == 4:
                self.assertEqual(data1.fields.CountryRegion, "United Kingdom")
                self._check_sorting_instance_data(data3, [
                        ['United Kingdom', 'Cambridge'],
                        ['United Kingdom', 'Cambridge']
                    ])
            elif i == 5:
                self.assertEqual(data1.fields.CountryRegion, "United States")
                self._check_sorting_instance_data(data3, [
                        ['United States', 'Albany'],
                        ['United States', 'Woodburn']
                    ])
            country_group.move_next()
            i += 1

    def _verify(self, report):
        self.assertNotEqual(report.data_sources['DataSourceTest'], None)
        self.assertEqual(report.data_sources['DataSourceTest'].name,
                         'DataSourceTest')

        # DataSet without filter
        data = report.data_sets['DataSet1']  # It is the DataInterface object
        # It is appended to the data_groups colecction too
        self.assertEqual('DataSet1' in report.data_sets,
                         'DataSet1' in report.data_groups)
        self.assertEqual(len(data.rows), 830)
        data.move_first()  # Move to first row
        self.assertEqual(data.EOF, False)

        i = 10248
        while not data.EOF:
            self.assertEqual(data.fields.id, i)
            self.assertEqual(data.fields.dummy, 'Dummy')
            self.assertEqual(data.fields.dummy_2, 'Dummy id ' + str(i))
            i += 1
            data.move_next()
        self.assertEqual(data.EOF, True)

        # DataSet filtered
        data = report.data_sets['DataSetFiltered']
        self.assertEqual(len(data.rows), 827)
        data.move_first()
        i = 10248
        while not data.EOF:
            if i in (10248, 10249, 11077):
                self.assertNotEqual(data.fields.id, i)
                i += 1
                continue
            self.assertEqual(data.fields.id, i)
            self.assertEqual(data.fields.dummy2, 'Dummy')
            self.assertEqual(data.fields.dummy_22, 'Dummy id ' + str(i))
            self.assertEqual(data.fields.dummy_property, str(i))
            self.assertEqual(data.fields.dummy_property_2, str(i))
            i += 1
            data.move_next()

        # Sort by id 'Descending'
        data = report.data_sets['DataSetSort1']
        data.move_first()
        x = 11077
        while not data.EOF:
            self.assertEqual(data.fields['id'], x)
            data.move_next()
            x -= 1

        # Sort by customer 'Descending' and date 'Ascending'
        data = report.data_sets['DataSetSort2']
        self.assertEqual(len(data.rows), 830)

        data.move_first()
        self.assertEqual(data.fields['customer'], 'WOLZA')
        self.assertEqual(data.fields['date'],
                         dateutil.parser.parse('1996-12-05'))

        data.move(100)
        self.assertEqual(data.fields['customer'], 'TORTU')
        self.assertEqual(data.fields['date'],
                         dateutil.parser.parse('1996-10-02'))
        data.move_last()
        self.assertEqual(data.fields['customer'], 'ALFKI')
        self.assertEqual(data.fields['date'],
                         dateutil.parser.parse('1998-04-09'))

        # ========== Groups ==================

        # Group is created automatically for each DataSet
        datasetgroup = report.data_groups['DataSet1']
        self.assertEqual(len(datasetgroup.instances), 1)
        self.assertEqual(len(datasetgroup.sub_group), 1)  # Tablix1 group
        self.assertEqual(datasetgroup.parent, None)  # Top Group
        self.assertEqual(datasetgroup.is_detail_group, False)
        # Orderred by id (defined in sql query)
        data = datasetgroup.instances[0].data
        self.assertEqual(data.row_count(), 830)
        data.move_first()
        self.assertEqual(data.fields.customer, "VINET")
        self.assertEqual(data.fields.freight, 32.38)
        data.move(400)
        self.assertEqual(data.fields.customer, "RICAR")
        self.assertEqual(data.fields.freight, 14.25)
        data.move_last()
        self.assertEqual(data.fields.customer, "RATTC")
        self.assertEqual(data.fields.freight, 8.53)

        # DataRegion group.
        # Created for each DataRegion (Tablix, Chart)
        # Data is filtered id > 10500
        # Data is sortered customer Descending and freight Ascending
        tablixgroup = report.data_groups['Tablix1']
        self.assertEqual(tablixgroup.parent, datasetgroup)
        self.assertEqual(len(tablixgroup.instances), 1)
        self.assertEqual(len(tablixgroup.sub_group), 2)  # Group1 and Group2
        self.assertEqual(tablixgroup.is_detail_group, False)
        data = tablixgroup.instances[0].data
        self.assertEqual(data.row_count(), 577)
        data.move_first()
        self.assertEqual(data.fields.customer, "WOLZA")
        self.assertEqual(data.fields.freight, 8.72)
        data.move(400)
        self.assertEqual(data.fields.customer, "GODOS")
        self.assertEqual(data.fields.freight, 175.32)
        data.move_last()
        self.assertEqual(data.fields.customer, "ALFKI")
        self.assertEqual(data.fields.freight, 69.53)

        # Group1
        group1 = report.data_groups['Group1']
        self.assertEqual(group1.parent, tablixgroup)
        self.assertEqual(len(group1.instances), 1)
        self.assertEqual(len(group1.sub_group), 0)
        self.assertEqual(tablixgroup.sub_group[0], group1)
        self.assertEqual(group1.is_detail_group, True)
        # Data equal to parent (Tablix1)
        data = group1.instances[0].data
        self.assertEqual(data.row_count(), 577)
        data.move_first()
        self.assertEqual(data.fields.customer, "WOLZA")
        self.assertEqual(data.fields.freight, 8.72)
        data.move(400)
        self.assertEqual(data.fields.customer, "GODOS")
        self.assertEqual(data.fields.freight, 175.32)
        data.move_last()
        self.assertEqual(data.fields.customer, "ALFKI")
        self.assertEqual(data.fields.freight, 69.53)

        # Group by date and sorted by customer ascending
        group2 = report.data_groups['Group2']
        # Adjacent group of Group1
        self.assertEqual(group2.parent, tablixgroup)
        self.assertEqual(len(group2.instances), 281)
        # DetailGroup
        self.assertEqual(len(group2.sub_group), 1)
        self.assertEqual(group2.is_detail_group, False)
        row_count = 0
        i = 0
        for ins in group2.instances:
            row_count += ins.data.row_count()
            if i == 0:
                self._check_instance_data(ins.data, [
                        ['BLAUS', 8.85], ['BLAUS', 8.85]
                    ])
            if i == 100:
                self._check_instance_data(ins.data, [
                        ['HUNGO', 142.33], ['QUEDE', 45.54]
                    ])
            if i == 203:
                ins.data.move_first()
                self._check_instance_data(ins.data, [
                        ['LINOD', 2.71], ['TRADH', 35.43]
                    ])
            if i == 280:
                self._check_instance_data(ins.data, [
                        ['BONAP', 38.28], ['SIMOB', 18.44]
                    ])
            i += 1
        self.assertEqual(row_count, 577)

        # DetailGroup
        # customer sorted Descending
        detailgroup = report.data_groups['DetailGroup']
        self.assertEqual(detailgroup.parent, group2)
        self.assertEqual(len(detailgroup.instances), 281)
        self.assertEqual(len(detailgroup.sub_group), 0)
        self.assertEqual(detailgroup.is_detail_group, True)
        row_count = 0
        i = 0
        for ins in detailgroup.instances:
            row_count += ins.data.row_count()
            if i == 0:
                self._check_instance_data(ins.data, [
                        ['BLAUS', 8.85], ['BLAUS', 8.85]
                    ])
            if i == 100:
                self._check_instance_data(ins.data, [
                        ['QUEDE', 45.54], ['HUNGO', 142.33]
                    ])
            if i == 203:
                self._check_instance_data(ins.data, [
                        ['TRADH', 35.43], ['LINOD', 2.71]
                    ])
            if i == 280:
                self._check_instance_data(ins.data, [
                        ['SIMOB', 18.44], ['BONAP', 38.28]
                    ])
            i += 1
        self.assertEqual(row_count, 577)

    def _check_sorting_instance_data(self, data, values):
        self._check_instance(data, values, ['CountryRegion', 'City'])

    def _check_instance_data(self, data, values):
        self._check_instance(data, values, ['customer', 'freight'])

    def _check_instance(self, data, values, fields):
        data.move_first()
        i = 0
        for field in fields:
            self.assertEqual(data.fields[fields[i]], values[0][i])
            i += 1
        data.move_last()
        i = 0
        for field in fields:
            self.assertEqual(data.fields[fields[i]], values[1][i])
            i += 1

    def _get_xml_string_1(self):
        return r'''
<Nuntiare>
  <Name>Data_Test</Name>
  <Width>21cm</Width>
  <Page></Page>
  <DataSources>
    <DataSource>
      <Name>DataSourceTest</Name>
      <ConnectionProperties>
        <DataProvider>=P.data_provider</DataProvider>
        <ConnectObject>=P.conn_string</ConnectObject>
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
          <DataType>Integer</DataType>
        </Field>
        <Field>
          <Name>date</Name>
          <DataField>orderdate</DataField>
          <DataType>DateTime</DataType>
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
          <DataType>Float</DataType>
        </Field>
        <Field>
          <Name>dummy</Name>
          <Value>Dummy</Value>
        </Field>
        <Field>
          <Name>dummy_2</Name>
          <Value>='Dummy id ' + str(F.id)</Value>
        </Field>
      </Fields>
      <Query>
        <DataSourceName>DataSourceTest</DataSourceName>
        <CommandText>SELECT orderid, orderdate, customerid,
employeeid, freight FROM orders ORDER BY orderid</CommandText>
      </Query>
    </DataSet>
    <DataSet>
      <Name>DataSetFiltered</Name>
      <Fields>
        <Field>
          <Name>id</Name>
          <DataField>orderid</DataField>
          <DataType>Integer</DataType>
        </Field>
        <Field>
          <Name>date2</Name>
          <DataField>orderdate</DataField>
          <DataType>DateTime</DataType>
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
          <DataType>Float</DataType>
        </Field>
        <Field>
          <Name>dummy2</Name>
          <Value>Dummy</Value>
        </Field>
        <Field>
          <Name>dummy_22</Name>
          <Value>='Dummy id ' + str(F['id'])</Value>
        </Field>
        <Field>
          <Name>dummy_property</Name>
          <Value>=str(F.id)</Value>
        </Field>
        <Field>
          <Name>dummy_property_2</Name>
          <Value>=str(F.id)</Value>
        </Field>
      </Fields>
      <Query>
        <DataSourceName>DataSourceTest</DataSourceName>
        <CommandText>SELECT orderid, orderdate, customerid,
employeeid, freight FROM orders ORDER BY orderid</CommandText>
      </Query>
      <Filters>
        <Filter>
          <FilterExpression>=F.id</FilterExpression>
          <Operator>NotEqual</Operator>
          <FilterValues>
            <FilterValue>=int(10248)</FilterValue>
          </FilterValues>
        </Filter>
        <Filter>
          <FilterExpression>=F.id</FilterExpression>
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
          <DataType>Integer</DataType>
        </Field>
        <Field>
          <Name>date</Name>
          <DataField>orderdate</DataField>
          <DataType>DateTime</DataType>
        </Field>
      </Fields>
      <Query>
        <DataSourceName>DataSourceTest</DataSourceName>
        <CommandText>SELECT orderid, orderdate
          FROM orders ORDER BY orderid</CommandText>
      </Query>
      <SortExpressions>
        <SortExpression>
          <Value>=F.id</Value>
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
          <DataType>Integer</DataType>
        </Field>
        <Field>
          <Name>date</Name>
          <DataField>orderdate</DataField>
          <DataType>DateTime</DataType>
        </Field>
        <Field>
          <Name>customer</Name>
          <DataField>customerid</DataField>
        </Field>
      </Fields>
      <Query>
        <DataSourceName>DataSourceTest</DataSourceName>
        <CommandText>SELECT orderid, orderdate, customerid
          FROM orders ORDER BY orderid</CommandText>
      </Query>
      <SortExpressions>
        <SortExpression>
          <Value>=F.customer</Value>
          <SortDirection>Descending</SortDirection>
        </SortExpression>
        <SortExpression>
          <Value>=F.date</Value>
        </SortExpression>
      </SortExpressions>
    </DataSet>
  </DataSets>
  <ReportParameters>
    <ReportParameter>
      <Name>data_provider</Name>
      <DataType>String</DataType>
      <DefaultValue>postgresql</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>conn_string</Name>
      <DataType>String</DataType>
      <DefaultValue>xxx</DefaultValue>
    </ReportParameter>
  </ReportParameters>
  <Body>
    <Height>300in</Height>
    <ReportItems>
      <Tablix>
        <Name>Tablix1</Name>
        <DataSetName>DataSet1</DataSetName>
        <Filters>
          <Filter>
            <FilterExpression>=F.id</FilterExpression>
            <Operator>GreaterThan</Operator>
            <FilterValues>
              <FilterValue>=int(10500)</FilterValue>
            </FilterValues>
          </Filter>
        </Filters>
        <SortExpressions>
          <SortExpression>
            <Value>=F.customer</Value>
            <SortDirection>Descending</SortDirection>
          </SortExpression>
          <SortExpression>
            <Value>=F.freight</Value>
          </SortExpression>
        </SortExpressions>
        <TablixColumnHierarchy>
          <TablixMembers>
            <TablixMember />
          </TablixMembers>
        </TablixColumnHierarchy>
        <TablixRowHierarchy>
          <TablixMembers>
            <TablixMember>
              <Group>
                <Name>Group1</Name>
              </Group>
            </TablixMember>
            <TablixMember>
              <Group>
                <Name>Group2</Name>
                <GroupExpressions>
                  <GroupExpression>=F.date</GroupExpression>
                </GroupExpressions>
                <SortExpressions>
                  <SortExpression>
                    <Value>=F.date</Value>
                  </SortExpression>
                  <SortExpression>
                    <Value>=F.customer</Value>
                  </SortExpression>
                </SortExpressions>
              </Group>
              <TablixMembers>
                <TablixMember>
                  <Group>
                    <Name>DetailGroup</Name>
                    <SortExpressions>
                      <SortExpression>
                        <Value>=F.customer</Value>
                        <SortDirection>Descending</SortDirection>
                      </SortExpression>
                      <SortExpression>
                        <Value>=F.freight</Value>
                        <SortDirection>Descending</SortDirection>
                      </SortExpression>
                    </SortExpressions>
                  </Group>
                </TablixMember>
              </TablixMembers>
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
            <TablixRow>
              <Height>0.42in</Height>
              <TablixCells>
                <TablixCell />
              </TablixCells>
            </TablixRow>
          </TablixRows>
        </TablixBody>
      </Tablix>
    </ReportItems>
  </Body>
</Nuntiare>
'''

    def _get_xml_string_2(self):
        return r'''
<Nuntiare>
  <Name>Sorting Test</Name>
  <Width>21cm</Width>
  <Page></Page>
  <ReportParameters>
    <ReportParameter>
      <Name>data_provider</Name>
      <DataType>String</DataType>
      <DefaultValue>postgresql</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>conn_string</Name>
      <DataType>String</DataType>
      <DefaultValue>xxx</DefaultValue>
    </ReportParameter>
  </ReportParameters>
  <DataSources>
    <DataSource>
      <Name>DataSourceTest</Name>
      <ConnectionProperties>
        <DataProvider>=P.data_provider</DataProvider>
        <ConnectObject>=P.conn_string</ConnectObject>
      </ConnectionProperties>
    </DataSource>
  </DataSources>
  <Body>
    <ReportItems>
      <Tablix>
        <Name>Tablix1</Name>
        <DataSetName>DataSet1</DataSetName>
        <TablixColumnHierarchy>
          <TablixMembers>
            <TablixMember/>
          </TablixMembers>
        </TablixColumnHierarchy>
        <TablixRowHierarchy>
          <TablixMembers>
            <TablixMember>
              <Group>
                <Name>Country</Name>
                <GroupExpressions>
                  <GroupExpression>=Fields.CountryRegion</GroupExpression>
                </GroupExpressions>
                <SortExpressions>
                  <SortExpression>
                    <Value>=Fields.CountryRegion</Value>
                    <SortDirection>Ascending</SortDirection>
                  </SortExpression>
                </SortExpressions>
              </Group>
              <TablixMembers>
                <TablixMember>
                  <Group>
                    <Name>Details</Name>
                    <SortExpressions>
                      <SortExpression>
                        <Value>=Fields.City</Value>
                      </SortExpression>
                    </SortExpressions>
                  </Group>
                </TablixMember>
              </TablixMembers>
            </TablixMember>
          </TablixMembers>
        </TablixRowHierarchy>
        <TablixBody>
          <TablixColumns>
            <TablixColumn>
              <Width>2in</Width>
            </TablixColumn>
          </TablixColumns>
          <TablixRows>
            <TablixRow>
              <Height>0.3in</Height>
              <TablixCells>
                <TablixCell>
                  <CellContents />
                </TablixCell>
              </TablixCells>
            </TablixRow>
          </TablixRows>
        </TablixBody>
      </Tablix>
    </ReportItems>
  </Body>

  <DataSets>
    <DataSet>
      <Name>DataSet1</Name>
      <Query>
        <DataSourceName>DataSourceTest</DataSourceName>
        <CommandText>SELECT address.addressline1, address.addressline2,
address.city, address.postalcode,
stateprovince.name as stateprovince, countryregion.name as countryregion
FROM address
INNER JOIN stateprovince
ON address.stateprovinceid = stateprovince.stateprovinceid
INNER JOIN countryregion
ON countryregion.countryregioncode = stateprovince.countryregioncode
ORDER BY address.addressid
LIMIT 500</CommandText>
      </Query>
      <Fields>
        <Field>
          <Name>AddressLine1</Name>
          <DataField>addressline1</DataField>
        </Field>
        <Field>
          <Name>AddressLine2</Name>
          <DataField>addressline2</DataField>
        </Field>
        <Field>
          <Name>City</Name>
          <DataField>city</DataField>
        </Field>
        <Field>
          <Name>StateProvince</Name>
          <DataField>stateprovince</DataField>
        </Field>
        <Field>
          <Name>PostalCode</Name>
          <DataField>postalcode</DataField>
        </Field>
        <Field>
          <Name>CountryRegion</Name>
          <DataField>countryregion</DataField>
        </Field>
      </Fields>
    </DataSet>
  </DataSets>
</Nuntiare>
'''
