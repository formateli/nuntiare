# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import os


def get_report_path(report_file):
    report_path = os.path.dirname(os.path.realpath(__file__))
    report_path = os.path.normpath(
        os.path.join(report_path, '..', 'report'))
    report_path = os.path.join(
        report_path, report_file)
    return report_path
