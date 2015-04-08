# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import sys 
import os

DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.normpath(os.path.join(DIR, '../..', 'nuntiare'))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import logging    
import unittest
import data_providers
import expression
import parameter
import data
import report

logging.basicConfig(filename='nuntiare_test.log',level=logging.DEBUG)

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(data_providers)
suite.addTests(loader.loadTestsFromModule(expression))
suite.addTests(loader.loadTestsFromModule(parameter))
suite.addTests(loader.loadTestsFromModule(data))
suite.addTests(loader.loadTestsFromModule(report))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

