# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys
import dateutil
import datetime
import math
from decimal import Decimal
from .. import logger

__data__=[None] # 0:report

def get_expression_eval(report, code):
    __data__[0]=report
    P = {} # Parameters
    G = {} # Globals
    M = {} # Modules
    if report:
        P = report.parameters
        G = report.globals
        M = report.parser.object.modules
    if report.current_scope:
        F = report.data_groups[report.current_scope] # Fields
        if F.EOF():
            F.move_first()
        if report.current_scope in report.parser.object.report_items_group:
            ReportItems = report.report_def.report_items_group[report.current_scope]

    try:
        result = eval(code)
    except KeyError as e:
        logger.error(
            "Error evaluating expression: '{0}'. Key does not exist in dictionary. <{1}>.".format(
                code, e.message),
            True, "ValueError")
    except:
        logger.error("Unexpected error evaluating expression: '{0}'. {1}.".format(code, sys.exc_info()[0]),
            True)

    return result 


def Data(scope=None):
    if not scope:
        return __data__[0].data_groups[__data__[0].current_scope]
    if not scope in __data__[0].data_groups:
        raise KeyError("Data group with name '{0}' not found.".format(scope))
    return __data__[0].data_groups[scope]

