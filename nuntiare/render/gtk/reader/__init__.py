# This file is part of Nuntiare project. 
# The COPYRIGHT file at the top level of this repository 
# contains the full copyright notices and license terms.

from nuntiare.render.render import Render
from gtk_reader import GtkReader

def get_render_object():
    return GtkReaderRender()

class GtkReaderRender(Render):
    def __init__(self):
        super(GtkReaderRender, self).__init__()

    def render(self, report):
        GtkReader(report)

    def help(self):
        "GtkReaderRender help"

