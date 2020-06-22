# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import os


def _get_current_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_report_path(report_file):
    report_path = os.path.normpath(
        os.path.join(_get_current_path(), '..', 'report'))
    report_path = os.path.join(
        report_path, report_file)
    return report_path


def get_data_path(data_file):
    data_path = os.path.normpath(
        os.path.join(_get_current_path(), '..', 'data'))
    data_path = os.path.join(
        data_path, data_file)
    return data_path


def get_test_path(file_):
    result = os.path.join(
        _get_current_path(), file_)
    return result
