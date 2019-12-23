# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Pluma unittest suite"

import os
import sys
import unittest

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.normpath(os.path.join(DIR, '..', '..', '..', 'nuntiare'))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import logging
import memento

logging.basicConfig(filename='pluma_test.log', level=logging.DEBUG)

LOADER = unittest.TestLoader()

SUITE = LOADER.loadTestsFromModule(memento)
#SUITE.addTests(LOADER.loadTestsFromModule(expression))

RUNNER = unittest.TextTestRunner(verbosity=2)
RESULT = RUNNER.run(SUITE)
