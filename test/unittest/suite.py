# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Nuntiare unittest suite"

import logging
import unittest
import load_module
import dataprovider
import expression
import parameter
import grid
import data
import aggregate
import render_pdf


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
