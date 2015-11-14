# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

class Error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Warning(Exception):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class InternalError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class DataError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass


class Connect(object):

    def __init__(self, connection_object, string_format):
        con_error = "Connection string not valid!. Its format must be: '{0}'".format(
            string_format)

        if connection_object == None or connection_object == "": 
            raise OperationalError(con_error)

        self.connection_object = connection_object

        self.parameters_dict = {}
        
        try:
            connection_object = connection_object.strip()
            i = connection_object.find('=')
            if (i < 0):
                raise OperationalError(con_error)
            self.parameters_dict = self._get_parameters(connection_object)
        except:
            pass

        self.is_closed = False
        self.cursors = []

    def cursor(self):
        raise NotImplementedError("cursor method must be overriden.")

    def commit(self):
        if self.is_closed:
            raise InterfaceError("Connection is closed!")

    def close(self):
        for c in self.cursors:
            del c
        del self.cursors
        self.is_closed = True  

    def _get_parameters(self, connection_string):
        pairs = connection_string.split(',')
        parameters = {} 
        for p in pairs:
            p = p.strip()
            para = p.split('=')
            parameters[para[0].strip()] = para[1].strip()
        return parameters


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
            raise InterfaceError("Cursor is closed!")
