# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
from nuntiare.report import Report

class ReportTest(unittest.TestCase):
    def testReport(self):
        r = Report("report_test.xml")

        self.assertEqual(r.get_element('Author').value(), 'Fredy Ramirez', "Author must be 'Fredy Ramirez'")
        self.assertEqual(r.get_element('Description').value(), 'Report test', "Description must be 'Report test'")
        self.assertEqual(r.get_element('XXXX'), None, "'None' if element does not exist")

        lnk = r.definition
        self.assertEqual(lnk.lnk.parent, None, "Not top element")
        self.assertEqual(lnk.lnk.obj, r.definition, "Not top element")
        self.assertEqual(lnk.lnk.report, r, "Not top element")

        lnk = r.get_element('ReportParameters')
        self.assertNotEqual(lnk, None, "Element must be 'ReportParameters' not 'None'")
        self.assertEqual(lnk.lnk.parent, r.definition, "Parent must be report")
        self.assertEqual(lnk.lnk.obj, lnk, "obj must be a ReportParameters object")
        self.assertEqual(lnk.lnk.report, r, "Report must be report")

        lnk2=lnk.get_element('ReportParameter')
        self.assertNotEqual(lnk2, None, "Element must be 'ReportParameter' not 'None'")
        self.assertEqual(lnk2.lnk.report, r, "Report must be report")
        self.assertEqual(lnk2.lnk.obj, lnk2, "obj must be a ReportParameter object")
        self.assertEqual(lnk2.lnk.parent, lnk, "Parent must be a ReportParameters element")

        self.assertEqual(len(r.parameters), 2, "len(r.parameters) must be '2'")

        self.assertEqual(r.parameters['parameter_1'], "parameter_value_1", "Value of 'parameter_1' must be 'parameter_value_1'")
        self.assertEqual(r.parameters['parameter_2'], "parameter_value_2", "Value of 'parameter_2' must be 'parameter_value_2'")

