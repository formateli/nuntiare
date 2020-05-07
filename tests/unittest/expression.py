# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import unittest
from nuntiare.definition.expression import (
        String, Boolean,
        Integer, Color, Size)
from nuntiare.report import Report


class ElementTypeTest(unittest.TestCase):
    def testElementType(self):
        string_xml = r"""
            <Nuntiare>
                <Name>Element Type Test</Name>
                <Width>21cm</Width>
                <Page></Page>
                <Body>
                    <Height>300in</Height>
                </Body>
            </Nuntiare>"""

        report = Report(string_xml)
        report.run()

        # String
        s = String(None, lnk=None, must_be_constant=True)
        self.assertEqual(s.value(report), None)
        s = String("Hello world!", True)
        self.assertEqual(s.value(report), "Hello world!", )
        s = String("= 'abc' + 'def'", False)  # Eval Expression
        self.assertEqual(s.value(report), "abcdef")

        # Boolean
        s = Boolean(None, True)
        self.assertEqual(s.value(report), None)
        s = Boolean("true", True)
        self.assertEqual(s.value(report), True)
        s = Boolean("false", True)
        self.assertEqual(s.value(report), False)
        s = Boolean("=False", False)
        self.assertEqual(s.value(report), False)
        s = Boolean("Y", True)
        self.assertEqual(s.value(report), True)
        s = Boolean("", True)
        self.assertEqual(s.value(report), False)
        s = Boolean("Xxs", True)
        self.assertEqual(s.value(report), False)
        s = Boolean("='true'", False)
        self.assertEqual(s.value(report), True)
        s = Boolean("=True", False)
        self.assertEqual(s.value(report), True)

        # Integer
        s = Integer(None, True)
        self.assertEqual(s.value(report), None)
        s = Integer("0", True)
        self.assertEqual(s.value(report), 0)
        s = Integer("=3.2", False)
        self.assertEqual(s.value(report), 3)
        s = Integer("-1", True)
        self.assertEqual(s.value(report), -1)

        # Size
        s = Size(None, True)
        self.assertEqual(s.value(report), 0.0)
        s = Size('10pt', True)
        self.assertEqual(s.value(report), 10.0)
        s = Size('10 pt', True)
        self.assertEqual(s.value(report), 10.0)
        s = Size('10', True)
        self.assertEqual(s.value(report), 10.0)
        s = Size('1in', True)
        self.assertEqual(s.value(report), 72.0)
        s = Size.convert(72.0, 'pt', 'in')
        self.assertEqual(s, 1)

        # Color
        s = Color(None, True)
        self.assertEqual(s.value(report), '#000000')
        s = Color('Black', True)
        self.assertEqual(s.value(report), '#000000')
        s = Color('Blue', True)
        self.assertEqual(s.value(report), '#0000FF')
        s = Color('IndianRed', True)
        self.assertEqual(s.value(report), '#CD5C5C')

        err_message = None
        try:
            rgb = Color.to_rgb('#FFCD5C5C')
        except Exception as e:
            err_message = e.args[0]
        self.assertEqual(
            err_message, "Color '#FFCD5C5C' not in correct format.")

        rgb = Color.to_rgb('#CD5C5C')
        self.assertEqual(rgb[0], 205)
        self.assertEqual(rgb[1], 92)
        self.assertEqual(rgb[2], 92)

        s = Color("SlateBlue", True)
        rgb = Color.to_rgb(s.value(report))
        self.assertEqual(rgb[0], 106)
        self.assertEqual(rgb[1], 90)
        self.assertEqual(rgb[2], 205)
