# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

import gtk
from viewer_widget import ViewerWidget

class GtkReader(gtk.Window):

    def __init__(self, report):
        super(GtkReader, self).__init__()        
        self.set_title("Nuntiare report")
        name=report.get_element('Name')
        if name:
            self.set_title(name.value())
        #self.set_size_request(report.get_element('PageHeight').get_value_in_unit('pt'), 
        #    report.get_element('PageWidth').get_value_in_unit('pt'))

        self.set_size_request(300, 300)

        self.set_position(gtk.WIN_POS_CENTER)

        self.connect("destroy", gtk.main_quit)

        viewer = ViewerWidget(report)
        self.add(viewer)

        self.show_all()
        gtk.main()
    

