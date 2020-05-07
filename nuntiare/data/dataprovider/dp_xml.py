# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from xml.dom.minidom import parse
from nuntiare import logger
from nuntiare.tools import get_xml_tag_value
from . definition import Connect, Cursor, InterfaceError


apilevel = '2.0'
paramstyle = 'pyformat'


class connect(Connect):
    def __init__(self, connection_string):
        super(connect, self).__init__(
            connection_string, 'file=[path/xmlFile.xml]')
        self.xmlfile = self.parameters_dict['file']

    def cursor(self):
        c = XmlCursor(self)
        self.cursors.append(c)
        return c


class XmlCursor(Cursor):
    def __init__(self, connection):
        super(XmlCursor, self).__init__(connection)

    def execute(self, operation, parameters=None):
        super(XmlCursor, self).execute(operation, parameters)

        dom = parse(self.connection.xmlfile)
        if not dom:
            raise InterfaceError(
                "DOM object could not be created from file '{0}'".formta(
                    self.connection.xmlfile))

        self.description = ()
        self.result = []
        count = 0

        query_info = self.get_query_info(operation, parameters)

        rows = dom.getElementsByTagName(query_info['table_name'])
        for row in rows:
            record = ()
            for d in row.childNodes:
                if count == 0:
                    if '*' in query_info['field_names']:  # Get all colummns
                        self.add_description(d.nodeName)
                    else:  # Only column(s) in SELECT
                        if d.nodeName in query_info['field_names']:
                            self.add_description(d.nodeName)

                if '*' in query_info['field_names']:
                    record = record + (get_xml_tag_value(d), )
                else:
                    if d.nodeName in query_info['field_names']:
                        record = record + (get_xml_tag_value(d), )
            self.result.append(record)
            count = count + 1

        # TODO cerrar dom y liberar recursos

        if count == 0:
            self.description = None
            self.result = None
        else:
            self.rowcount = count

        return self.result

    def get_query_info(self, operation, parameters):
        '''
        Get fields name, table name and where conditions from query
        '''

        operation = operation.strip()

        i_from = operation.upper().find(' FROM ')
        if i_from < 0:
            err_msg = "Wrong SQL format. "
            err_msg += "'FROM' statement must be in query. {0}"
            raise InterfaceError(err_msg.format(operation))

        select_str = operation[:6].upper() + operation[6:i_from]

        if not select_str.startswith('SELECT'):
            err_msg = "Wrong SQL format. "
            err_msg += "'SELECT' statement must be in query. {0}"
            raise InterfaceError(err_msg.format(operation))

        fields = select_str[6:].split(',')
        i = 0
        for f in fields:
            fields[i] = f.strip()
            i += 1

        result = {}
        result['field_names'] = fields

        from_str = operation[i_from+6:].strip()

        i_where = operation.upper().find(' WHERE ')
        if i_where < 0:
            table_name = from_str
        else:
            # TODO - parameters
            logger.warning(
                "'WHERE' statement not supported by nuntiare at this moment.")
            table_name = from_str[:i_where]

        result['table_name'] = table_name
        return result

    def add_description(self, column_name):
        desc = ()
        desc = desc + (column_name, None)
        self.description = self.description + (desc,)
