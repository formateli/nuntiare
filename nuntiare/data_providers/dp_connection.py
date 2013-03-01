# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from dp_exceptions import InterfaceError, OperationalError

class Connect:

    def __init__(self, connection_string, string_format):
 
        con_error = "Connection string not valid!. Its format must be: '" + string_format  + "'"

        if connection_string == None or connection_string == "": 
            raise OperationalError(con_error)

        connection_string = connection_string.strip()

        i = connection_string.find('=')
        if (i < 0):
            raise OperationalError(con_error)

        self.parameters_dict = self.get_parameters(connection_string)
        if not self.parameters_dict.has_key('file'):
            raise OperationalError("Parameter 'file' must be defined in connection string.")
        #TODO: verificar que el archivo existe
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

    def get_parameters(self, connection_string):
        pairs = connection_string.split(',')
        parameters = {} 
        for p in pairs:
            p = p.strip()
            para = p.split('=')
            parameters[para[0].strip()] = para[1].strip()
        return parameters        


