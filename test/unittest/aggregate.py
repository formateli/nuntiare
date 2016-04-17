# -*- coding: utf-8 -*-
# This file is part of Nuntiare project.
# The COYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import unittest
import os
from datetime import datetime
from decimal import Decimal
from nuntiare.report import Report
from nuntiare.definition.functions import *


class AggregateTest(unittest.TestCase):
    def test_aggregate(self):
        '''
        Test a simple table (Tablix with just a TablixBody)
        and aggregates Count, RunningValue, RowNumber, and
        Sum in diferent contexts.
        Test Grouping and sorting too.
        '''

        report_path = os.path.dirname(os.path.realpath(__file__))
        report_path = os.path.normpath(
            os.path.join(report_path, '..', 'report'))
        report = Report(os.path.join(
            report_path, 'northwind_orders.xml'))

        con_file_info = open("db_test_connection_northwind", "r")
        conn_str = con_file_info.readline()
        con_file_info.close()

        parameters = {'conn_string': conn_str}
        report.run(parameters)

        grid = report.result.body.items.item_list[0].grid_body

        self.assertEqual(self._cell_value(grid, 0, 2), 'Product')
        self.assertEqual(self._cell_value(grid, 0, 11), 'Running Avg')

        # Austria
        self._ckeck_country_header(
            grid, 1, 7, 1, 'Austria', 305.00,
            4483.4, 994.72, 3488.68, 7, 3488.68, 498.38)
        self._ckeck_customer_header(
            grid, 2, 1, 'Ernst Handel', 305.00,
            4483.4, 994.72, 3488.68, 7, 3488.68, 498.38)
        self._ckeck_order_header(grid, 3, 1, 10258)
        self._ckeck_order_line(
            grid, 4, 1, 'Chang', 50.0,
            15.2, 760.0, 0.2, 152.0, 608.0, 1, 608.0, 608.0, 1)
        self._ckeck_order_line(
            grid, 6, 3, 'Mascarpone Fabioli', 6.0,
            25.6, 153.6, 0.2, 30.72, 122.88, 3, 1614.88, 538.29, 3)
        self._ckeck_order_footer(
            grid, 7, 3, 3, 3, 2018.6, 4483.4, 4483.4,
            1614.88, 1614.88, 1614.88, 10258)
        self._ckeck_order_header(grid, 8, 2, 10263)
        self._ckeck_order_line(
            grid, 10, 5, 'Longlife Tofu', 36.0,
            8.0, 288.0, 0.25, 72.0, 216.0, 2, 316.8, 158.4, 5)
        self._ckeck_order_line(
            grid, 12, 7, 'Pavlova', 60.0,
            13.9, 834.0, 0.25, 208.50, 625.5, 4, 1873.8, 468.45, 7)
        self._ckeck_order_footer(
            grid, 13, 4, 7, 7, 2464.8, 4483.4, 4483.4,
            1873.8, 3488.68, 3488.68, 10263)

        # Brazil
        self._ckeck_country_header(
            grid, 21, 20, 3, 'Brazil', 229.0,
            4223.6, 260.4, 3963.2, 10, 3963.2, 396.32)
        self._ckeck_customer_header(
            grid, 22, 1, 'Hanari Carnes', 162.00,
            3257.8, 260.4, 2997.4, 6, 2997.4, 499.57)
        self._ckeck_order_header(grid, 23, 1, 10250)
        self._ckeck_order_line(
            grid, 24, 11, "Jack's New England Clam Chowder", 10.0,
            7.7, 77.0, 0.0, 0.0, 77.0, 1, 77.0, 77.0, 11)
        self._ckeck_order_line(
            grid, 26, 13, "Manjimup Dried Apples", 35.0,
            42.4, 1484.0, 0.15, 222.6, 1261.4, 3, 1552.6, 517.53, 13)
        self._ckeck_order_footer(
            grid, 27, 3, 3, 3, 1813.0, 3257.8, 4223.6,
            1552.6, 1552.6, 1552.6, 10250)
        self._ckeck_order_footer(
            grid, 32, 3, 6, 6, 1444.8, 3257.8, 4223.6,
            1444.8, 2997.4, 2997.4, 10253)
        self._ckeck_customer_header(
            grid, 33, 2, 'Que Delícia', 40.0,
            448.0, 0.0, 448.0, 2, 448.0, 224.0)
        self._ckeck_order_footer(
            grid, 37, 2, 2, 8, 448.0, 448.0, 4223.6,
            448.0, 448.0, 3445.4, 10261)
        self._ckeck_customer_header(
            grid, 38, 3, "Wellington Importadora", 27.0,
            517.8, 0.0, 517.8, 2, 517.8, 258.9)
        self._ckeck_order_line(
            grid, 41, 20, "Perth Pasties", 15.0,
            26.2, 393.0, 0.0, 0.0, 393.0, 2, 517.8, 258.9, 20)
        self._ckeck_order_footer(
            grid, 42, 2, 2, 10, 517.8, 517.8, 4223.6,
            517.8, 517.8, 3963.2, 10256)

        # Venezuela
        self._ckeck_country_header(
            grid, 200, 100, 13, 'Venezuela', 136.0,
            3635.9, 0.0, 3635.9, 9, 3635.9, 403.99)
        self._ckeck_customer_header(
            grid, 201, 1, "GROSELLA-Restaurante", 14.0,
            1101.2, 0.0, 1101.2, 2, 1101.2, 550.6)
        self._ckeck_order_line(
            grid, 203, 92, "Mozzarella di Giovanni", 4.0,
            27.8, 111.2, 0.0, 0.0, 111.2, 1, 111.2, 111.2, 92)
        self._ckeck_order_footer(
            grid, 205, 2, 2, 2, 1101.2, 1101.2, 3635.9,
            1101.2, 1101.2, 1101.2, 10268)
        self._ckeck_order_footer(
            grid, 218, 4, 4, 9, 1414.8, 1414.8, 3635.9,
            1414.8, 1414.8, 3635.9, 10283)

    def _ckeck_order_footer(
            self, grid, row,
            v1, v2, v3, v4, v5, v6, v7, v8, v9, v10):
        # RowNumber('orderid')
        self.assertEqual(self._cell_value(grid, row, 1), v1)
        # RowNumber('customer')
        self.assertEqual(self._cell_value(grid, row, 2), v2)
        # RowNumber('country')
        self.assertEqual(self._cell_value(grid, row, 3), v3)
        # Sum('F.subtotal1')
        self.assertEqual(round(self._cell_value(grid, row, 4), 2), v4)
        # Sum('F.subtotal1', 'customer')
        self.assertEqual(round(self._cell_value(grid, row, 5), 2), v5)
        # Sum('F.subtotal1', 'country')
        self.assertEqual(round(self._cell_value(grid, row, 6), 2), v6)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'orderid')
        self.assertEqual(round(self._cell_value(grid, row, 7), 2), v7)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'customer')
        self.assertEqual(round(self._cell_value(grid, row, 8), 2), v8)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'country')
        self.assertEqual(round(self._cell_value(grid, row, 9), 2), v9)
        # F.orderid
        self.assertEqual(self._cell_value(grid, row, 10), v10)

    def _ckeck_order_line(
            self, grid, row,
            v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12):
        # RowNumber('TablixOrder')
        self.assertEqual(self._cell_value(grid, row, 0), v1)
        # F.product
        self.assertEqual(self._cell_value(grid, row, 2), v2)
        # F.quantity
        self.assertEqual(self._cell_value(grid, row, 3), v3)
        # F.unitprice
        self.assertEqual(self._cell_value(grid, row, 4), v4)
        # F.subtotal1
        self.assertEqual(round(self._cell_value(grid, row, 5), 2), v5)
        # F.discount
        self.assertEqual(self._cell_value(grid, row, 6), v6)
        # F.discount_amount
        self.assertEqual(round(self._cell_value(grid, row, 7), 2), v7)
        # F.subtotal1 - F.discount_amount
        self.assertEqual(round(self._cell_value(grid, row, 8), 2), v8)
        # RowNumber('orderid')
        self.assertEqual(self._cell_value(grid, row, 9), v9)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'orderid')
        self.assertEqual(round(self._cell_value(grid, row, 10), 2), v10)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Avg', 'orderid')
        self.assertEqual(round(self._cell_value(grid, row, 11), 2), v11)
        # RowNumber('TablixOrder')
        self.assertEqual(self._cell_value(grid, row, 12), v12)

    def _ckeck_order_header(self, grid, row, v1, v2):
        # RunningValue('F.orderid','CountDistinct','customer')
        self.assertEqual(self._cell_value(grid, row, 1), v1)
        # F.orderid
        self.assertEqual(self._cell_value(grid, row, 2), v2)

    def _ckeck_customer_header(
            self, grid, row,
            v1, v2, v3, v4, v5, v6, v7, v8, v9):
        # RunningValue('F.customer', 'CountDistinct', 'country')
        self.assertEqual(self._cell_value(grid, row, 1), v1)
        # F.customer
        self.assertEqual(self._cell_value(grid, row, 2), v2)
        # Sum('F.quantity')
        self.assertEqual(self._cell_value(grid, row, 3), v3)
        # Sum('F.subtotal1')
        self.assertEqual(self._cell_value(grid, row, 5), v4)
        # Sum('F.discount_amount')
        self.assertEqual(self._cell_value(grid, row, 7), v5)
        # Sum('F.subtotal1 - F.discount_amount')
        self.assertEqual(round(self._cell_value(grid, row, 8), 2), v6)
        # RowNumber('customer')
        self.assertEqual(self._cell_value(grid, row, 9), v7)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'customer')
        self.assertEqual(round(self._cell_value(grid, row, 10), 2), v8)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Avg', 'customer')
        self.assertEqual(round(self._cell_value(grid, row, 11), 2), v9)

    def _ckeck_country_header(
            self, grid, row,
            v1, v2, v3, v4, v5, v6, v7, v8, v9, v10):
        # RowNumber() in Tablix contexts (Counting countries)
        self.assertEqual(self._cell_value(grid, row, 0), v1)
        # RunningValue('F.country', 'CountDistinct')
        self.assertEqual(self._cell_value(grid, row, 1), v2)
        # F.country
        self.assertEqual(self._cell_value(grid, row, 2), v3)
        # Sum('F.quantity')
        self.assertEqual(self._cell_value(grid, row, 3), v4)
        # Sum('F.subtotal1')
        self.assertEqual(self._cell_value(grid, row, 5), v5)
        # Sum('F.discount_amount')
        self.assertEqual(self._cell_value(grid, row, 7), v6)
        # Sum('F.subtotal1 - F.discount_amount')
        self.assertEqual(round(self._cell_value(grid, row, 8), 2), v7)
        # RowNumber('country')
        self.assertEqual(self._cell_value(grid, row, 9), v8)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Sum', 'country')
        self.assertEqual(round(self._cell_value(grid, row, 10), 2), v9)
        # RunningValue('F.subtotal1 - F.discount_amount', 'Avg', 'country')
        self.assertEqual(round(self._cell_value(grid, row, 11), 2), v10)

    def _cell_value(self, grid, row, column):
        cell = grid.get_cell(row, column)
        return cell.object.item_list[0].value

    def test_functions(self):
        # Conversion functions
        self.assertEqual(CBool('true'), True)
        self.assertEqual(CBool('t'), True)

        self.assertEqual(
            CDate('20151231'), datetime(2015, 12, 31, 0, 0, 0))
        self.assertEqual(
            CDate('20151231 23:59:59'), datetime(2015, 12, 31, 23, 59, 59))

        self.assertEqual(CInt('1'), 1)
        self.assertEqual(CInt(1.1), 1)

        self.assertEqual(CFloat('1.1'), 1.1)
        self.assertEqual(CInt(CFloat('1.1')), 1)

        self.assertEqual(CDecimal('1.1'), Decimal('1.1'))
        self.assertEqual(CDecimal(1.1), Decimal(1.1))

        self.assertEqual(CStr(1.1), '1.1')
        self.assertEqual(CStr(True), 'True')
        self.assertEqual(
            CStr(datetime(2015, 12, 31, 0, 0, 0)), '2015-12-31 00:00:00')

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
        self.assertEqual(Day(datetime(2015, 12, 31, 23, 15, 49)), 31)
        self.assertEqual(Month(datetime(2015, 12, 31, 23, 15, 49)), 12)
        self.assertEqual(Year(datetime(2015, 12, 31, 23, 15, 49)), 2015)
        self.assertEqual(Hour(datetime(2015, 12, 31, 23, 15, 49)), 23)
        self.assertEqual(Minute(datetime(2015, 12, 31, 23, 15, 49)), 15)
        self.assertEqual(Second(datetime(2015, 12, 31, 23, 15, 49)), 49)
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
        self.assertEqual(
            Replace(replace_test, 'abc', 'xxx'), 'xxx def xxx hij klm')
        self.assertEqual(
            Replace(replace_test, 'abc', 'xxx', 1), 'xxx def abc hij klm')

        self.assertEqual(String(5, 'x'), 'xxxxx')
        self.assertEqual(String(0, 'x'), '')
