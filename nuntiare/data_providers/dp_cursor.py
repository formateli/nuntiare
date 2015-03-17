# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from . dp_exceptions import InterfaceError

class Cursor(object):
    def __init__(self, connection):
        self.connection = connection
        self.rowcount = -1
        self.is_closed = False
        self.description = None
        self.result = None

    def execute(self, operation, parameters=None):
        self.verify_close()
        self.result = None
        self.description= None  

    def fetchone(self):
        self.verify_close()
        raise NotImplementedError("fetchone not supported. Use fetchall instead.")

    def fetchall(self):
        self.verify_close()
        return self.result

    def close(self):
        del self.rowcount
        del self.description
        del self.result 
        self.is_closed = True

    def verify_close(self):
        if self.is_closed:
            raise ex.InterfaceError("Cursor is closed!")

