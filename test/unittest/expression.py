# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
from nuntiare.template.expression import String, Boolean, Integer
from nuntiare.report import Report

class ElementTypeTest(unittest.TestCase):
    def testElementType(self):
    
        string_xml="""
            <Report>
                <Name>Element Type Test</Name>
                <Width>21cm</Width>
                <Page></Page>
                <Body>
                    <Height>300in</Height>
                </Body>
            </Report>"""
    
        report = Report(string_xml)        
        report.run()
    
        # String
        s = String(None, True)
        self.assertEqual(s.value(report), None, "string 0")
        s = String("Hello world!", True)
        self.assertEqual(s.value(report), "Hello world!", "string 1")
        s = String("= 'abc' + 'def'", False) # Eval Expression
        self.assertEqual(s.value(report), "abcdef", "string 2")

        # Boolean
        s = Boolean(None, True)
        self.assertEqual(s.value(report), None, "Boolean 0")
        s = Boolean("true", True)
        self.assertEqual(s.value(report), True, "Boolean 1")
        s = Boolean("false", True)
        self.assertEqual(s.value(report), False, "Boolean 2")
        s = Boolean("=False", False)
        self.assertEqual(s.value(report), False, "Boolean 3")
        s = Boolean("Y", True)
        self.assertEqual(s.value(report), True, "Boolean 4")        
        s = Boolean("", True)
        self.assertEqual(s.value(report), False, "Boolean 5")
        s = Boolean("Xxs", True)
        self.assertEqual(s.value(report), False, "Boolean 6")
        s = Boolean("='true'", False)
        self.assertEqual(s.value(report), True, "Boolean 7")        
        s = Boolean("=True", False)
        self.assertEqual(s.value(report), True, "Boolean 8")                
        
        # Integer
        s = Integer(None, True)
        self.assertEqual(s.value(report), None, "Integer 0")
        s = Integer("0", True)
        self.assertEqual(s.value(report), 0, "Integer 1") 
        s = Integer("=3.2", False)
        self.assertEqual(s.value(report), 3, "Integer 2")
        s = Integer("-1", True)
        self.assertEqual(s.value(report), -1, "Integer 3")

