# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from element import Element

class DataSets(Element):
    def __init__(self, node, lnk):
        elements={'DataSet': [Element.ELEMENT],}
        super(DataSets, self).__init__(node, elements, lnk) 


class DataSet(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Fields': [Element.ELEMENT],
                  'Query': [Element.ELEMENT],
                  'Filters': [Element.ELEMENT], #TODO
                 }
        super(DataSet, self).__init__(node, elements, lnk)


class Fields(Element):
    def __init__(self, node, lnk):
        elements={'Field': [Element.ELEMENT],}
        super(Fields, self).__init__(node, elements, lnk) 


class Field(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'DataField': [Element.STRING],
                  'Value': [Element.VARIANT],
                 }
        super(Field, self).__init__(node, elements, lnk)


class Query(Element):
    def __init__(self, node, lnk):
        elements={'DataSourceName': [Element.STRING],
                  'CommandText': [Element.STRING],
                  'QueryParameters': [Element.ELEMENT],
                 }
        super(Query, self).__init__(node, elements, lnk)


class QueryParameters(Element):
    def __init__(self, node, lnk):
        elements={'QueryParameter': [Element.ELEMENT],}
        super(QueryParameters, self).__init__(node, elements, lnk) 


class QueryParameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING],
                  'Value': [Element.VARIANT],
                 }
        super(QueryParameter, self).__init__(node, elements, lnk)

