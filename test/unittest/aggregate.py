# This file is part of Nuntiare project. 
# The COYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import unittest
from datetime import datetime
from decimal import Decimal
from nuntiare.definition.functions import *

class AggregateTest(unittest.TestCase):
    def test_functions(self):
    
        # Conversion functions
        self.assertEqual(CBool('true'), True)
        self.assertEqual(CBool('t'), True)

        self.assertEqual(CDate('20151231'), datetime(2015,12,31,0,0,0))
        self.assertEqual(CDate('20151231 23:59:59'), datetime(2015,12,31,23,59,59))

        self.assertEqual(CInt('1'), 1)
        self.assertEqual(CInt(1.1), 1)

        self.assertEqual(CFloat('1.1'), 1.1)
        self.assertEqual(CInt(CFloat('1.1')), 1)

        self.assertEqual(CDecimal('1.1'), Decimal('1.1'))
        self.assertEqual(CDecimal(1.1), Decimal(1.1))

        self.assertEqual(CStr(1.1), '1.1')
        self.assertEqual(CStr(True), 'True')
        self.assertEqual(CStr(datetime(2015,12,31,0,0,0)), '2015-12-31 00:00:00')


        # Conditional functions
        self.assertEqual(Iif(True, 'a', 'b'), 'a')
        self.assertEqual(Iif(False, 'a', 'b'), 'b')
        self.assertEqual(Iif(None, 'a', 'b'), 'b')

        self.assertEqual(Switch(0, 0, 'a', 1, 'b', 2, 'c'), 'a')
        self.assertEqual(Switch(1, 0, 'a', 1, 'b', 2, 'c'), 'b')
        self.assertEqual(Switch(2, 0, 'a', 1, 'b', 2, 'c'), 'c')

        self.assertEqual(Choose(1, 'a', 'b', 'c'), 'a')
        self.assertEqual(Choose(2, 'a', 'b', 'c'), 'b')
        self.assertEqual(Choose(3, 'a', 'b', 'c'), 'c')


        # Date funtions
        self.assertEqual(Day(datetime(2015,12,31,23,15,49)), 31)
        self.assertEqual(Month(datetime(2015,12,31,23,15,49)), 12)
        self.assertEqual(Year(datetime(2015,12,31,23,15,49)), 2015)
        self.assertEqual(Hour(datetime(2015,12,31,23,15,49)), 23)
        self.assertEqual(Minute(datetime(2015,12,31,23,15,49)), 15)
        self.assertEqual(Second(datetime(2015,12,31,23,15,49)), 49)
        self.assertEqual(Day(Today()), Day(datetime.today()))


        # String funtions
        self.assertEqual(Format('Hello', 'Hello'), 'Hello')
        self.assertEqual(Format('World!', 'Hello {0}'), 'Hello World!')
        self.assertEqual(Format(12, '{:,.2f}'), '12.00')

        self.assertEqual(LCase('To Lower'), 'to lower')
        self.assertEqual(LCase(None), None)
        self.assertEqual(UCase('To Upper'), 'TO UPPER')
        self.assertEqual(UCase(None), None)
        self.assertEqual(Len(''), 0)
        self.assertEqual(Len('Get Lenght'), 10)
        self.assertEqual(Len(None), None)
        self.assertEqual(LTrim(''), '')
        self.assertEqual(LTrim('  '), '')
        self.assertEqual(LTrim(' LTrim'), 'LTrim')
        self.assertEqual(LTrim('       LTrim'), 'LTrim')
        self.assertEqual(LTrim('LTrim  '), 'LTrim  ')
        self.assertEqual(RTrim(''), '')
        self.assertEqual(RTrim('  '), '')
        self.assertEqual(RTrim('RTrim '), 'RTrim')
        self.assertEqual(RTrim('RTrim       '), 'RTrim')
        self.assertEqual(RTrim('  RTrim'), '  RTrim')
        self.assertEqual(Trim(''), '')
        self.assertEqual(Trim('  '), '')
        self.assertEqual(Trim(' Trim '), 'Trim')
        self.assertEqual(Trim('      Trim       '), 'Trim')

        mid_test = 'Mid Function Demo'
        self.assertEqual(Mid(mid_test, 1, 3), 'Mid')
        self.assertEqual(Mid(mid_test, 14, 4), 'Demo')
        self.assertEqual(Mid(mid_test, 5), 'Function Demo')
        self.assertEqual(Mid(mid_test, 5, 150), 'Function Demo')
        self.assertEqual(Mid(mid_test, 150), '')
        
        replace_test = 'abc def abc hij klm'
        self.assertEqual(Replace(replace_test, 'abc', 'xxx'), 'xxx def xxx hij klm')
        self.assertEqual(Replace(replace_test, 'abc', 'xxx', 1), 'xxx def abc hij klm')

        self.assertEqual(String(5, 'x'), 'xxxxx')
        self.assertEqual(String(0, 'x'), '')
        
