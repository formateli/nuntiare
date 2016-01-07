# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Nuntiare unittest suite"

import sys
import os

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.normpath(os.path.join(DIR, '../..', 'nuntiare'))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import logging
import unittest
import dataprovider
import expression
import parameter
import grid
import data
import aggregate

logging.basicConfig(filename='nuntiare_test.log', level=logging.DEBUG)

LOADER = unittest.TestLoader()

SUITE = LOADER.loadTestsFromModule(dataprovider)
SUITE.addTests(LOADER.loadTestsFromModule(expression))
SUITE.addTests(LOADER.loadTestsFromModule(parameter))
SUITE.addTests(LOADER.loadTestsFromModule(grid))
SUITE.addTests(LOADER.loadTestsFromModule(data))
SUITE.addTests(LOADER.loadTestsFromModule(aggregate))

RUNNER = unittest.TextTestRunner(verbosity=2)
RESULT = RUNNER.run(SUITE)

