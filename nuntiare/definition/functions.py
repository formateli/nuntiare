# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from datetime import datetime
from .. data.data_type import DataType


# Conversion functions
def CBool(value):
    'Converts to boolean'
    return DataType.get_value('Boolean', value)


def CDate(value):
    'Converts to datetime'
    return DataType.get_value('DateTime', value)


def CInt(value):
    'Converts to integer'
    return DataType.get_value('Integer', value)


def CFloat(value):
    'Converts to float'
    return DataType.get_value('Float', value)


def CDecimal(value):
    'Converts to decimal'
    return DataType.get_value('Decimal', value)


def CStr(value):
    'Converts to unicode string'
    return DataType.get_value('String', value)


# Conditional functions
def Iif(bool_exp, exp1, exp2):
    '''
    Evaluates bool_exp.
    If True returns exp1, else exp2
    '''
    return exp1 if bool_exp else exp2


def Switch(value, *result):
    '''
    Finds and returns the corresponding value
    in a result pair of possibilities, where first member
    of the pair is the key to compare value, and second member
    is the result value to return.
    '''
    i = 0
    while i < len(result):
        if result[i] == value:
            return result[i + 1]
        i += 2


def Choose(int_exp, *result):
    '''
    Lookup a value in a list of possiblities.
    int_expression is 1 base, which mean that
    int_exp=2 returns result[1]
    '''
    i = CInt(int_exp)
    return result[i - 1]


# Date funtions
def Day(date):
    'Returns the integer day of date.'
    return date.day


def Month(date):
    'Returns the integer month of date.'
    return date.month


def Year(date):
    'Returns the integer year of date.'
    return date.year


def Hour(date_time):
    'Returns the integer hour of date_time.'
    return date_time.hour


def Minute(date_time):
    'Returns the integer minute of date_time.'
    return date_time.minute


def Second(date_time):
    'Returns the integer second of date_time.'
    return date_time.second


def Today():
    'Returns the date time value of today.'
    return datetime.today()


def DayOfWeek(date_time):
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dayNumber=date_time.weekday()
    return days[dayNumber]


# String funtions
def Format(value, format_exp):
    'Formats value according to format_exp.'
    return format_exp.format(value)


def LCase(value):
    'Returns the lower case of the passed string'
    if value is None:
        return
    return value.strip().lower()


def UCase(value):
    'Returns the upper case of the passed string'
    if value is None:
        return
    return value.strip().upper()


def Len(value):
    'Returns the lenght of string'
    if value is None:
        return
    return len(value)


def LTrim(value):
    'Removes leading blanks from the passed string'
    if value is None:
        return
    while value.startswith(' '):
        value = value[1:]
    return value


def RTrim(value):
    'Removes trailing blanks from the passed string'
    if value is None:
        return
    while value.endswith(' '):
        value = value[:len(value) - 1]
    return value


def Trim(value):
    'Removes blanks from both sides of passed string'
    value = LTrim(value)
    value = RTrim(value)
    return value


def Mid(value, start=1, length=None):
    'Returns a substring'
    if value is None:
        return
    if start > len(value):
        return ''
    if length is None:
        return value[start - 1:]
    else:
        return value[start - 1: start - 1 + length]


def Replace(value, old, new, count=-1):
    'Replace substrings in the passed string'
    return value.replace(old, new, count)


def String(number, char):
    'Creates a new string with char repeated a number of times'
    if char is None:
        return
    value = '{:' + char + '<' + str(number) + '}'
    return Format('', value)
