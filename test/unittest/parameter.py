# This file is part of Nuntiare project. 
# The COYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
import dateutil
from decimal import Decimal
from nuntiare.definition.report_def import ReportDef
from nuntiare.report.report import Report

class ParameterTest(unittest.TestCase):
    def testData(self):
        report_def = ReportDef(string_xml = self.get_xml_string())        
        report = Report(report_def)
        
        # Get ReportParameters default values
        report.run() 
    
        self.assertEqual(report.parameters['para_bool'], True, "para_bool")
        self.assertEqual(report.parameters['para_integer'], -1, "para_integer")
        self.assertEqual(report.parameters['para_integer_exp'], 99, "para_integer_exp")
        self.assertEqual(report.parameters['para_float'], 0.01, "para_float")
        self.assertEqual(type(report.parameters['para_decimal']), Decimal, "para_decimal_1")
        self.assertEqual(round (report.parameters['para_decimal']), round(Decimal(0.09)), "para_decimal_2")
        self.assertEqual(report.parameters['para_string'], 'Hello', "para_string")
    
        # Pass parameters values    
        parameters={'para_bool':'false',
                    'para_string':'Hello World', 
                    'para_integer':'999', 
                    'para_decimal':'5.987432'}
        report.run(parameters)

        self.assertEqual(report.parameters['para_bool'], False, "para_bool")
        self.assertEqual(report.parameters['para_integer'], 999, "para_integer")
        self.assertEqual(report.parameters['para_integer_exp'], 1099, "para_integer_exp")        
        self.assertEqual(report.parameters['para_float'], 0.01, "para_float")
        self.assertEqual(type(report.parameters['para_decimal']), Decimal, "para_decimal_1")
        self.assertEqual(round (report.parameters['para_decimal']), round(Decimal(5.987432)), "para_decimal_2")
        self.assertEqual(report.parameters['para_string'], 'Hello World', "para_string")
    
    
        report.run() # Default values again
    
        self.assertEqual(report.parameters['para_bool'], True, "para_bool")
        self.assertEqual(report.parameters['para_integer'], -1, "para_integer")
        self.assertEqual(report.parameters['para_integer_exp'], 99, "para_integer_exp")
        self.assertEqual(report.parameters['para_float'], 0.01, "para_float")
        self.assertEqual(type(report.parameters['para_decimal']), Decimal, "para_decimal_1")
        self.assertEqual(round (report.parameters['para_decimal']), round(Decimal(0.09)), "para_decimal_2")
        self.assertEqual(report.parameters['para_string'], 'Hello', "para_string")    
    
    def get_xml_string(self):
        return '''
            <Nuntiare>
                <Name>Parameter test</Name>
                <Width>100in</Width>
                <Page></Page>
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
                        <DefaultValue>=Parameters['para_integer'] + 100</DefaultValue>                        
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
                </ReportParameters>
                <Body>
                    <Height>300in</Height>
                </Body>
            </Nuntiare>
            '''

