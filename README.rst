Nuntiare
========

**Nuntiare** (*Report* in latin) is a report toolkit written in python.
It is inspired by RDL (report definition language) specifications, 
but simplified and adapted to Python world.


At a glance
-----------

- Reports are defined using xml files as templates.
- Templates are processed to generate reports according to data (database, parameters, etc). 
  Nuntiare can connect to any database (modules implementing API 2.0) for data gathering.
- Reports can be saved as nuntiare files for later usage.
- Nuntiare defines a render API that can be implemented to develop custom ones.
  Nuntiare comes with following renders: pdf, png and svg (based on cairo), html, csv and xml.
- It comes with a comand line tool *(nuntiare)*. 


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

Process myreport.xml and saves it as myreport.nuntiare (report file)::

    nuntiare render myreport.xml --save

Loads myreport.nuntiare report file and rendres it to pdf::

    nuntiare render myreport.nuntiare -r pdf

Process myreport.xml passing two parameters, user and city, 
and then renders it to html.::

    nuntiare render myreport.xml -p user=framirez city=panama -r html

Converts myreport.rdl (Rdl 2008) to myreport.xml (nuntiare report definition)::

    nuntiare convert myreport.rdl


Setup
-----

Install::

    python setup.py install --record files.txt
    
Uninstall (Ubuntu)::

    sudo bash -c "cat files.txt | xargs rm -rf"

