Nuntiare
========

.. _Formateli: http://www.formateli.com/

**Nuntiare** (*Reporte* en latin) es un conjunto de herramientas para el diseño, ejecución 
y presentación de reportes escrito en Python.
Está inspirado por las especificaciones RDL (report definition language), 
pero simplificado y adaptado al mundo Python.

Entre algunas de sus características podemos citar:

* Los reportes son definidos usando archivos xml como plantillas.
* Las plantillas son procesadas para generar reportes de acuerdo a datos suministrados (base de datos, parámetros, etc).
* Nuntiare puede conectarse con cualquier origen de datos (módulos que implementen API 2.0) para la recopilación de datos. Objetos Python pueden pasarse como parámetros para actuar como DataSet.
* Nuntiare viene con los siguientes renders: pdf, png y svg (basados en cairo), html, csv y xml.
* Variedad de ReportItems: Textbox, Matrix, SubReport, Image, Chart, etc.
* Variedad de funciones incorporadas:
    - Agregados: Max, Min, Count, CountDistinct, CountRows, First, Last, Previous, Avg, Sum, StDevP, Var, VarP, RunningValue, RowNumber.
    - Funciones: CBool, CDate, CInt, CFloat, CDecimal, CStr, Iif, Switch, Choose, Day, Month, Year, Hour, Minute, Second, Today, Format, LCase, UCase, Len, Trim, RTrim, LTrim, Mid, Replace, String.
* Nuntiare viene con una herramienta de linea de comandos *(nuntiare)*. 


Indice
------

* Especificaciones.
* nuntiare, herramienta de linea de comando.
