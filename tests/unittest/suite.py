# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Nuntiare unittest suite"

import os
import sys
import unittest

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.normpath(os.path.join(DIR, '..', '..', 'nuntiare'))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import logging
import dataprovider
import expression
import parameter
import grid
import data
import aggregate
import render_pdf   # TODO should be a diferent library
                    # because it depends on GTK


logging.basicConfig(filename='nuntiare_test.log', level=logging.DEBUG)

LOADER = unittest.TestLoader()

SUITE = LOADER.loadTestsFromModule(dataprovider)
SUITE.addTests(LOADER.loadTestsFromModule(expression))
SUITE.addTests(LOADER.loadTestsFromModule(parameter))
SUITE.addTests(LOADER.loadTestsFromModule(grid))
SUITE.addTests(LOADER.loadTestsFromModule(data))
SUITE.addTests(LOADER.loadTestsFromModule(aggregate))
SUITE.addTests(LOADER.loadTestsFromModule(render_pdf))

RUNNER = unittest.TextTestRunner(verbosity=2)
RESULT = RUNNER.run(SUITE)
