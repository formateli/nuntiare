# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.data_providers import get_data_provider
import unittest

class DataProvidersTest(unittest.TestCase):
    def testDataProviders(self):
        dp = get_data_provider("no_name")
        self.assertEqual(dp, None, "DataProvider must be 'None'")

        f = open("db_test_connection_panama", "r")
        psql = f.readline()
        f.close()

        providers = {'xml':'file=../data/panama.xml',
                     'postgresql':psql,
                    }

        for name, connstr in providers.items():
            self.runTest(name, connstr)

    def runTest(self, name, connstr):
        dp = get_data_provider(name)
        self.assertNotEqual(dp, None, "No data provider for " + name)
        self.assertEqual(dp.apilevel, "2.0", "API must be 2.0 for: " + name)

        conn = dp.connect(connstr)
        cursor = conn.cursor()
        self.assertEqual(cursor.rowcount, -1, "cursor.rowcount must be -1 for: " + name)

        cursor.execute("SELECT * FROM city")

        self.assertEqual(len(cursor.description), 5, "Not 5 colummns for: " + name)
        self.assertEqual(cursor.description[0][0], 'id', "First column is not id for: " + name)

