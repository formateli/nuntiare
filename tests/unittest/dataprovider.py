# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from nuntiare.data.data import DataSource, DataSet
from nuntiare.data.dataprovider import get_data_provider
import unittest

"Nuntiare dataprovider test"


class DataProvidersTest(unittest.TestCase):
    def test_dataproviders(self):
        data_provider = get_data_provider('no_exists')
        self.assertEqual(data_provider, None)

        test_params = []

        conn_info_file = open('db_test_connection_panama', 'r')
        psql = conn_info_file.readline()
        conn_info_file.close()

        test_params.append(self._get_test_params(
                'postgresql',
                psql,
                'SELECT * FROM city'
                ))

        test_params.append(self._get_test_params(
                'xml',
                'file=../data/panama.xml',
                'SELECT * FROM city'
                ))

        from dataprovider_data import CITIES_OBJ, CITIES_LIST

        test_params.append(self._get_test_params(
                'object',
                CITIES_OBJ,
                None
                ))

        test_params.append(self._get_test_params(
                'object',
                CITIES_LIST,
                None
                ))

        for parameter in test_params:
            self._run_test(parameter)

    def _run_test(self, test_param):
        field_map = [
            {
                'name': 'id',
                'data_field': 'id',
                'field_value': None,
                'data_type': 'Integer'
            },
        ]

        data_provider = get_data_provider(test_param['data_provider_name'])
        self.assertNotEqual(data_provider, None, test_param['data_provider_name'])
        self.assertEqual(data_provider.apilevel, '2.0')

        data_source = DataSource(
                name='datasource1',
                data_provider=data_provider
                )
        data_source.connect(test_param['connection_object'])

        data_set = DataSet(
                report=None,
                name='ds1',
                data_source=data_source,
                field_map=field_map
                )
        self.assertEqual(data_set.row_count(), 0)
        self.assertEqual(data_set.EOF, True)

        data_set.execute(test_param['command'])

        self.assertEqual(data_set.row_count(), 15)

        # When just executed cursor points to first record
        # No needed to call move_first()
        self.assertEqual(data_set.EOF, False)
        i = 1
        while not data_set.EOF:
            self.assertEqual(data_set.fields.id, i)
            self.assertEqual(data_set.fields['id'], i)
            self.assertEqual(data_set.fields[0], i)
            self.assertEqual(data_set.fields('id', "Name"), "id")
            self.assertEqual(data_set.fields('id', "Value"), i)
            self.assertEqual(data_set.fields('id', "IsMissing"), False)
            self.assertEqual(data_set.fields('id', "DataType"), "Integer")
            self.assertEqual(data_set.row_number(), i)
            i += 1
            data_set.move_next()

        self.assertEqual(data_set.EOF, True)
        data_set.move_first()
        self.assertEqual(data_set.EOF, False)
        i = 1
        while not data_set.EOF:
            self.assertEqual(data_set.fields['id'], i)
            self.assertEqual(data_set.row_number(), i)
            i += 1
            data_set.move_next()

        data_set.move_last()
        self.assertEqual(data_set.EOF, False)
        self.assertEqual(data_set.fields['id'], 15)

        # Move is '0' base index.
        data_set.move(0)
        self.assertEqual(data_set.EOF, False)
        self.assertEqual(data_set.fields['id'], 1)
        data_set.move(5)
        self.assertEqual(data_set.EOF, False)
        self.assertEqual(data_set.fields['id'], 6)

        data_set.move(20)  # TODO Should raise error?
        self.assertEqual(data_set.EOF, True)

    @staticmethod
    def _get_test_params(name, connection_object, command):
        res = {
            'data_provider_name': name,
            'connection_object': connection_object,
            'command': command,
        }
        return res
