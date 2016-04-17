# This file is part of Nuntiare project.
# The COYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import unittest
import dateutil
import math
from decimal import Decimal
from nuntiare.report import Report


class ParameterTest(unittest.TestCase):
    def testParameters(self):
        report = Report(self._get_xml_string())

        # Get ReportParameters default values
        report.run()

        self.assertEqual(report.parameters.para_bool, True)
        self.assertEqual(report.parameters.para_integer, -1)

        # Diferent ways to use Collections in templates.
        # P['parameter_name'] --> Returns Value
        self.assertEqual(report.parameters.para_integer_exp, 99)
        # Parameters['parameter_name'] --> Returns Value
        self.assertEqual(report.parameters.para_integer_exp_2, 99)
        # P.parameter_name --> Returns Value
        self.assertEqual(report.parameters.para_integer_exp_3, 99)
        # Parameters.parameter_name --> Returns Value
        self.assertEqual(report.parameters.para_integer_exp_4, 99)
        # Parameters('parameter', 'Value') --> Returns Value
        self.assertEqual(report.parameters.para_integer_exp_5, 99)
        # Parameters('parameter_name', 'Name') --> Returns Name
        self.assertEqual(report.parameters.para_string_exp_6, 'para_integer')

        self.assertEqual(
            report.parameters['para_float'], 0.01)
        self.assertEqual(
            type(report.parameters['para_decimal']), Decimal)
        self.assertEqual(
            round(report.parameters['para_decimal']), round(Decimal(0.09)))
        self.assertEqual(
            report.parameters['para_string'], 'Hello')

        # Pass parameters values
        parameters = {
                        'para_bool': 'false',
                        'para_string': 'Hello World',
                        'para_integer': '999',
                        'para_decimal': '5.987432'
                    }
        report.run(parameters)

        self.assertEqual(report.parameters['para_bool'], False)
        self.assertEqual(report.parameters['para_integer'], 999)
        self.assertEqual(report.parameters['para_integer_exp'], 1099)
        self.assertEqual(report.parameters['para_float'], 0.01)
        self.assertEqual(
            type(report.parameters['para_decimal']), Decimal)
        self.assertEqual(
            round(report.parameters['para_decimal']),
            round(Decimal(5.987432)))
        self.assertEqual(report.parameters['para_string'], 'Hello World')

        report.run()  # Default values again

        self.assertEqual(report.parameters['para_bool'], True)
        self.assertEqual(report.parameters['para_integer'], -1)
        self.assertEqual(report.parameters['para_integer_exp'], 99)
        self.assertEqual(report.parameters['para_float'], 0.01)
        self.assertEqual(type(report.parameters['para_decimal']), Decimal)
        self.assertEqual(
            round(report.parameters['para_decimal']),
            round(Decimal(0.09)))
        self.assertEqual(report.parameters['para_string'], 'Hello')

        # Test Modules
        self.assertEqual(report.parameters.para_module_1, math.pi)
        self.assertEqual(report.parameters.para_module_2, math.e)

    def _get_xml_string(self):
        return '''
<Nuntiare>
  <Name>Parameter test</Name>
  <Width>100in</Width>
  <Page></Page>
  <Modules>
    <Module>
      <From>math</From>
      <Import>pi</Import>
      <As>pi_number</As>
    </Module>
    <Module>
      <Import>math</Import>
    </Module>
  </Modules>
  <ReportParameters>
    <ReportParameter>
      <Name>para_bool</Name>
      <DataType>Boolean</DataType>
      <DefaultValue>True</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_date</Name>
      <DataType>DateTime</DataType>
      <DefaultValue>2014-09-05</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer</Name>
      <DataType>Integer</DataType>
      <DefaultValue>-1</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer_exp</Name>
      <DataType>Integer</DataType>
      <DefaultValue>=P['para_integer'] + 100</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer_exp_2</Name>
      <DataType>Integer</DataType>
      <DefaultValue>=Parameters['para_integer'] + 100</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer_exp_3</Name>
      <DataType>Integer</DataType>
      <DefaultValue>=P.para_integer + 100</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer_exp_4</Name>
      <DataType>Integer</DataType>
      <DefaultValue>=Parameters.para_integer + 100</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_integer_exp_5</Name>
      <DataType>Integer</DataType>
      <DefaultValue>=Parameters('para_integer', 'Value') + 100</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_string_exp_6</Name>
      <DataType>String</DataType>
      <DefaultValue>=Parameters('para_integer', 'Name')</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_float</Name>
      <DataType>Float</DataType>
      <DefaultValue>0.01</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_decimal</Name>
      <DataType>Decimal</DataType>
      <DefaultValue>0.09</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_string</Name>
      <DataType>String</DataType>
      <DefaultValue>Hello</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_module_1</Name>
      <DataType>Float</DataType>
      <DefaultValue>=M.pi_number</DefaultValue>
    </ReportParameter>
    <ReportParameter>
      <Name>para_module_2</Name>
      <DataType>Float</DataType>
      <DefaultValue>=Modules.math.e</DefaultValue>
    </ReportParameter>
  </ReportParameters>
  <Body>
    <Height>300in</Height>
  </Body>
</Nuntiare>
'''
