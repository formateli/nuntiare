Nuntiare
========

*Nuntiare* (Report in latin) is a report toolkit written in python. 
It is inspired by RDL (report definition language) specifications, 
but simplified and adapted to Python world.


At a glance
-----------

- Reports are defined using xml files.
- Xml definition files are processed to generate reports. 
  Nuntiare can connect to any database (modules implementing API 2.0) for data gathering.
- Reports can be saved as nuntiare files for later usage.
- Nuntiare defines a render API that can be implemented to develop custom ones.
  Nuntiare comes with following renders: pdf, png and svg (based on cairo), html, csv and xml.
- It comes with a comand line tool (nuntiare). 
  It can run commands like 'render' (render to especific type), 
  'convert' (converts rdl 2008 to nuntiare), etc.


Usage
-----

The better form of knowing nuntiare is trough its command line tool.

For help::

    nuntiare -h

or::

    nuntiare render -h

Process line.xml (report definition file) and renders it to 
line.html and line.pdf::

    nuntiare render line.xml -r html pdf

Process line.xml and saves it as line.nuntiare (report file)::

    nuntiare render line.xml --save

Loads line.nuntiare report file and rendres it to pdf::

    nuntiare render line.nuntiare -r pdf

Process line.xml passing two parameters, user and city, 
and then renders it to html.::

    nuntiare render line.xml -p user=framirez city=panama -r html

Converts line.rdl (Rdl 2008) to line.xml (nuntiare report definition)::

    nuntiare convert line.rdl


Setup
-----

Install::
    python setup.py install --record files.txt
    
Uninstall (Ubuntu)::

    sudo bash -c "cat files.txt | xargs rm -rf"

