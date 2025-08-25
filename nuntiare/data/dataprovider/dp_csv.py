# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import csv
from . definition import Connect, Cursor

apilevel = '2.0'
paramstyle = 'pyformat'


class connect(Connect):
    def __init__(self, connection_string):
        super().__init__(
            connection_string, 'file=path/csvFile.csv[,delimeter=;, quotechar=", header=1]')
        self.csvfile = self.parameters_dict.get('file')
        self.delimeter = self.parameters_dict.get('delimeter', ',')
        self.quotechar = self.parameters_dict.get('quotechar', '"')
        self.header = self.parameters_dict.get('header', '0')

    def cursor(self):
        c = CsvCursor(self)
        self.cursors.append(c)
        return c


class CsvCursor(Cursor):
    def execute(self, operation, parameters=None):
        super().execute(operation, parameters)

        self.description = ()
        self.result = []
        count = 0

        with open(self.connection.csvfile, newline='') as csvfile:
            reader = csv.reader(csvfile,
                        delimiter=self.connection.delimeter,
                        quotechar=self.connection.quotechar)
            for row in reader:
                if count == 0 and self.connection.header == '1':
                    for r in row:
                        self.add_description(r)
                    count += 1
                    continue

                self.result.append(row)
                count += 1

        if count == 0:
            self.description = None
            self.result = None
        else:
            self.rowcount = count

        return self.result
