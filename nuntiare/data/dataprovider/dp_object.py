# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from . definition import Connect, Cursor

apilevel = '2.0'
paramstyle = 'pyformat'


class connect(Connect):
    def __init__(self, connection_object):
        super(connect, self).__init__(
            connection_object, 'A valid Python Object.')

    def cursor(self):
        c = ObjectCursor(self)
        self.cursors.append(c)
        return c


class ObjectCursor(Cursor):
    def __init__(self, connection):
        super(ObjectCursor, self).__init__(connection)

    def execute(self, operation, parameters=None):
        super(ObjectCursor, self).execute(operation, parameters)
        self.description = ()
        self.result = []
        if self.connection.connection_object:
            self.rowcount = len(self.connection.connection_object)
            for obj in self.connection.connection_object:
                self.result.append(obj)

        return self.result
