Nuntiare
========

**Nuntiare** (*Report* in latin) is a report toolkit written in python.
It is inspired by RDL (report definition language) specifications, 
but simplified and adapted to Python world.


At a glance
-----------

- Reports are defined using xml files as templates.
- Templates are processed to generate reports according to data (database, parameters, etc). 
- Nuntiare can connect to any database (modules implementing API 2.0) for data gathering. Python object can be passed trough paramters to be a dataset.
- Nuntiare comes with following renders: html, csv and xml. - pdf, png and svg (based on cairo) planned.
- ReportItems: Line, Rectangle, Textbox and Matrix. - SubReport, Image and Chart Planned.
- Embedded Functions:
    - Aggregates: Max, Min, Count, CountDistinct, CountRows, First, Last, Previous, Avg, Sum, StDevP, Var, VarP, RunningValue, RowNumber.
    - Functions: CBool, CDate, CInt, CFloat, CDecimal, CStr, Iif, Switch, Choose, Day, Month, Year, Hour, Minute, Second, Today, Format, LCase, UCase, Len, Trim, RTrim, LTrim, Mid, Replace, String.
- Nuntiare comand line tool *(nuntiare)*.
- Nuntiare WYSWYG report designer *(pluma)*. Planned.


Usage
-----

The best way of knowing nuntiare is trough its command line tool.

For help::

    nuntiare -h

or::

    nuntiare render -h

Process myreport.xml (report definition file) and renders it to 
myreport.html and myreport.pdf::

    nuntiare render myreport.xml -r html pdf

Process myreport.xml and saves it as myreport.nuntiare (with data appended)::

    nuntiare render myreport.xml --save

Process myreport.nuntiare and renders it to pdf.
This file has tha data appended to it, 
if database connection fails then data is loaded from it.::

    nuntiare render myreport.nuntiare -r pdf

Process myreport.xml passing two parameters, user and city, 
and then renders it to html.::

    nuntiare render myreport.xml -p user=framirez city=panama -r html

Converts myreport.rdl (Rdl 2008) to myreport.xml (nuntiare report definition). It is an experimental feature.::

    nuntiare convert myreport.rdl


Setup
-----

Install::

    python setup.py install


Documentation
-------------

https://formateli.com/nuntiare


Version
-------

Current version: 0.3.1-alpha


Roadmap
-------

0.1.0

   * Data from databases (API 2.0), csv, xml, lists and objects.
   * Dataset Group and Order.


0.2.0

   * Aggregates: Max, Min, Count, CountDistinct, CountRows, First, Last,
     Previous, Avg, Sum, RunningValue, RowNumber.
   * Functions: CBool, CDate, CInt, CFloat, CDecimal, CStr, Iif, Switch,
     Choose, Day, Month, Year, Hour, Minute, Second, Today, Format, LCase,
     UCase, Len, Trim, RTrim, LTrim, Mid, Replace, String.


0.3.0

   * Controls:
      - Textbox
      - Line
      - Rectangle
      - Tablix
   * html, csv and xml renders.
   * Full *nuntiare* command line tool implemented.


0.4.0

   * *pluma* report designer.
      - Designer view.
      - Xml view.
      - Run and export view.

0.5.0

   * pdf, png and svg renders (Cairo based).


0.6.0

   * Controls:
      - Image
      - Sub report.


0.7.0

   * Chart control.


0.8.0

   * *pluma* report designer.
      - Viewer plugin.
