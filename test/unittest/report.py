# This file is part of Nuntiare project. 
# The COYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
import os
from nuntiare.report import Report

class ReportTest(unittest.TestCase):
    def testReport(self):
        report1 = Report(self._get_xml_report())
        self.assertEqual(report1.parser.type, "xml_template")
        self._verify(report1)
        
        report1.save(True)

        f_result = os.path.join(report1.globals['output_directory'], 
                report1.globals['output_name'] + ".nuntiare")
                
        report2 = Report(f_result)
        self.assertEqual(report2.parser.type, "xml_outcome")
        self._verify(report2)

        os.remove(f_result)

    def _verify(self, report):
        report.run()
        self.assertEqual(report.parameters['param_1'], "Param string")
        self.assertEqual(report.parameters['param_2'], 3289.25)
        self.assertEqual(report.result.height, 220.0)
        self.assertEqual(report.result.width, 210.0)
        self.assertEqual(report.result.header.height, 10.0)
        self.assertEqual(report.result.footer.height, 15.0)

    def _get_xml_report(self):
        return '''
            <Report>
                <Name>Report_Test</Name>
                <Page>
                    <PageHeight>220mm</PageHeight>
                    <PageWidth>210mm</PageWidth>
                    <PageHeader>
                        <Height>10mm</Height>
                    </PageHeader>
                    <PageFooter>
                        <Height>15mm</Height>
                    </PageFooter>                    
                </Page>
                
                <ReportParameters>
                    <ReportParameter>
                        <Name>param_1</Name>
                        <DataType>String</DataType>
                        <DefaultValue>Param string</DefaultValue>
                    </ReportParameter>
                    <ReportParameter>
                        <Name>param_2</Name>
                        <DataType>Float</DataType>
                        <DefaultValue>3289.25</DefaultValue>
                    </ReportParameter>
                </ReportParameters>

                <Body>
                    <ReportItems>
                        <Textbox>
                            <Name>Textbox1</Name>
                            <Value>=P['param_1']</Value>
                        </Textbox>
                    </ReportItems>
                </Body>
            </Report>
            '''
 
