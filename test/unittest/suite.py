# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import sys, os
try:
    DIR = os.path.dirname(os.path.realpath(__file__))
    DIR = os.path.normpath(os.path.join(DIR, '../..', 'nuntiare'))
    if os.path.isdir(DIR):
        sys.path.insert(0, os.path.dirname(DIR))
except NameError:
    pass

import logging
logging.basicConfig(filename='nuntiare_test.log',level=logging.DEBUG)
    
import unittest
import data_providers
import expression
import parameter
import data

loader = unittest.TestLoader()

suite = loader.loadTestsFromModule(data_providers)
suite.addTests(loader.loadTestsFromModule(expression))
suite.addTests(loader.loadTestsFromModule(parameter))
suite.addTests(loader.loadTestsFromModule(data))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

