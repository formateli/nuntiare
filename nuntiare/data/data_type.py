# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from sys import version_info
from dateutil import parser
from datetime import date, datetime
from decimal import Decimal
from .. import LOGGER


class DataType():
    @staticmethod
    def get_value(data_type, value):
        def _to_bool(value):
            if value is None:
                return
            if isinstance(value, bool):
                return value

            if str(value).lower() in \
                    ('yes', 'y', 'true',  't', '1', '-1'):
                return True
            if str(value).lower() in \
                    (
                        'no',  'n', 'false', 'f',
                        '0', '0.0', '', 'none', '[]', '{}'):
                return False

            LOGGER.warn(
                "Unknown bool expression '{0}'. False assigned.".format(value))
            return False

        if data_type is None or value is None:
            return value

        types = (
                    'Boolean',
                    'DateTime',
                    'Integer',
                    'String',
                    'Float',
                    'Decimal',
                    'Object'
                )

        if data_type not in types:
            err_msg = "Unknown Data Type '{0}' for expression '{1}'. " \
                "Data type must be: {2}"
            LOGGER.error(err_msg.format(data_type, value, types), True)

        if data_type == 'Object':
            return value

        result = None

        try:
            if data_type == 'Boolean':
                result = _to_bool(value)
            if data_type == 'DateTime':
                if isinstance(value, datetime):
                    result = value
                elif isinstance(value, date):
                    result = datetime.combine(value, datetime.min.time())
                else:
                    result = parser.parse(value)
            if data_type == 'Integer':
                result = int(value)
            if data_type == 'String':
                try:
                    result = str(value)  # Python3 always return unicode
                except UnicodeEncodeError:
                    result = value.encode('utf-8')

                if version_info[0] == 2:  # if python2
                    if isinstance(value, unicode):
                        result = value.encode('utf-8')


#                try:
#                    result = str(value)  # Python3 always return unicode
#                except UnicodeEncodeError:
#                    result = value.encode('utf-8')
#                if version_info[0] == 2:  # if python2, Convert to unicode
#                    if isinstance(result, unicode):
#                        pass
#                    elif isinstance(result, str):
#                        result = unicode(result, 'utf-8')
#                    else:
#                        result = unicode(str(result), 'utf-8')

            if data_type == 'Float':
                result = float(value)
            if data_type == 'Decimal':
                result = Decimal(value)

        except Exception as e:
            LOGGER.error(
                "Error getting value '{0}' for '{1}'. {2}".format(
                    value, data_type, e.args),
                True)

        return result
