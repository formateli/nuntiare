# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import sys
import os
import logging


DIR = os.path.dirname(os.path.realpath(__file__))
UNITTEST_DIR = os.path.normpath(os.path.join(DIR, '..', 'unittest'))
DIR = os.path.normpath(os.path.join(DIR, '..', '..', 'nuntiare'))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))


from nuntiare import LOGGER                 # noqa: E402
from nuntiare.report import Report          # noqa: E402
from nuntiare.render.render import Render   # noqa: E402


def get_conn_string(file_name):
    con_file_info = open(
        os.path.join(UNITTEST_DIR, file_name), 'r')
    conn_str = con_file_info.readline()
    con_file_info.close()
    return conn_str


REPORTS = {
    'countries1.xml': [['xml', 'html', 'csv'], {}],
    'countries2.xml': [['xml', 'html', 'csv'], {}],
    'image.xml': [['html'], {}],
    'grid.xml': [['xml', 'html'], {}],
    'keep_together_1.xml': [['xml', 'html', 'pdf'], {}],
    'keep_together_2.xml': [['xml', 'html', 'pdf'], {}],
    'keep_together_3.xml': [['xml', 'html', 'pdf'], {}],
    'line.xml': [['xml', 'html', 'pdf'], {}],
    'northwind_orders.xml': [['xml', 'html', 'csv'], {
        'conn_string': get_conn_string('db_test_connection_northwind')}],
    'reportviewer_tablix_sample1.xml': [['xml', 'html'], {
        'conn_string': get_conn_string('db_test_connection_adventure')}],
    'reportviewer_tablix_sample2.xml': [['xml', 'html'], {
        'conn_string': get_conn_string('db_test_connection_adventure')}],
    'reportviewer_tablix_sample3.xml': [['xml', 'html'], {
        'conn_string': get_conn_string('db_test_connection_adventure')}],
    'rownumber.xml': [['html'], {}],
    'tablix_example_1.xml': [['xml', 'html'], {
       'conn_string': get_conn_string('db_test_connection_adventure')}],
    'tablix_example_2.xml': [['xml', 'html'], {
        'conn_string': get_conn_string('db_test_connection_adventure')}],
    'tablix_example_3.xml': [['xml', 'html'], {
        'conn_string': get_conn_string('db_test_connection_adventure')}],
    'text.xml': [['xml', 'html', 'pdf'], {}],
    'text2.xml': [['xml', 'html', 'pdf'], {}],
}


def run_report(report_file, renders, parameters):

    LOGGER.info('file: {0}'.format(report_file))

    if not os.path.isfile(report_file):
        LOGGER.critical(
            "File '{0}' not found.".format(report_file),
            True, 'IOError')

    report = Report(report_file, output_name=report_file)
    report.run(parameters)
    for r in renders:
        LOGGER.info("render '{0}'".format(r))
        render = Render.get_render(r)
        if not render:
            LOGGER.warn(
                "Render '{0}' not found.".format(r))
            continue
        render.render(report, True)


def run_reports(report_file):
    if sys.stdout:
        LOGGER.add_handler(logging.StreamHandler(sys.stdout), 'DEBUG')

    LOGGER.info('Running Reports Tests...')

    if report_file:
        if report_file not in REPORTS:
            LOGGER.error(
                "File '{0}' not in list to test.".format(report_file), True)
        run_report(
            report_file,
            REPORTS[report_file][0],
            REPORTS[report_file][1])
        return

    for key, value in REPORTS.items():
        LOGGER.info(
            "Running '{0}' report".format(key))
        run_report(key, value[0], value[1])


if __name__ == "__main__":
    report_file = None
    if len(sys.argv) > 1:
        report_file = sys.argv[1]
    run_reports(report_file)
