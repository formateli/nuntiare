# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.        
        
class Subreport(ReportItem):
    def __init__(self, node, lnk):
        elements={'ReportName': [Element.STRING, True],
                  'Parameters': [Element.ELEMENT],
                  'NoRowsMessage': [Element.STRING],
                  'MergeTransactions': [Element.BOOLEAN, True],
                  'KeepTogether': [Element.BOOLEAN, True],
                  'OmitBorderOnPageBreak': [Element.BOOLEAN, True],
                 }
        super(Subreport, self).__init__("Subreport", node, lnk, elements)


class Parameters(Element):
    def __init__(self, node, lnk):
        elements={'Parameter': [Element.ELEMENT],}
        super(Parameters, self).__init__(node, elements, lnk) 


class Parameter(Element):
    def __init__(self, node, lnk):
        elements={'Name': [Element.STRING, True],
                  'Value': [Element.VARIANT],
                  'Omi': [Element.BOOLEAN],        
                 }
        super(Parameter, self).__init__(node, elements, lnk) 

