# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
from nuntiare.template.expression import String, Boolean, Integer, \
        Color, Size
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

        # Size
        s = Size(None, True)
        self.assertEqual(s.value(report), 0.0, "Size None")
        s = Size('10mm', True)
        self.assertEqual(s.value(report), 10.0, "Size '10mm'")
        s = Size('10 mm', True)
        self.assertEqual(s.value(report), 10.0, "Size '10 mm'")
        s = Size('1in', True)
        self.assertEqual(s.value(report), 25.4, "Size '1in'")
        s = Size.convert(25.4, 'mm', 'in')
        self.assertEqual(s, 1, "Size.convert((25.4,'mm','in'))")

        # Color
        s = Color(None, True)
        self.assertEqual(s.value(report), '#000000', "Color None")
        s = Color('Black', True)
        self.assertEqual(s.value(report), '#000000', "Color 'Black'")
        s = Color('Blue', True)
        self.assertEqual(s.value(report), '#0000FF', "Color 'Blue'") 
        s = Color('IndianRed', True)
        self.assertEqual(s.value(report), '#CD5C5C', "Color 'IndianRed'") 
        
        er = None
        try:
            rgb = Color.to_rgb('#FFCD5C5C')
        except Exception as e:
            er = e.message
        self.assertEqual(er, "Color '#FFCD5C5C' not in correct format.")
        
        rgb = Color.to_rgb('#CD5C5C')
        self.assertEqual(rgb[0], 205) 
        self.assertEqual(rgb[1], 92) 
        self.assertEqual(rgb[2], 92)
        
        s = Color("SlateBlue", True)
        rgb = Color.to_rgb(s.value(report))
        self.assertEqual(rgb[0], 106) 
        self.assertEqual(rgb[1], 90) 
        self.assertEqual(rgb[2], 205)
        
