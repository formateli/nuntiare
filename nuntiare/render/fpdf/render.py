# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from fpdf import FPDF
from .. render import Render
from ... import LOGGER


class FPdfRender(Render):
    def __init__(self):
        super(FPdfRender, self).__init__(extension='pdf')

    def render(self, report, **kws):
        super(FPdfRender, self).render(report, **kws)
        pdf = FPDF(unit='pt',
                   format=(report.result.width, report.result.height))
        author = report.definition.Author
        if author is not None:
            pdf.set_author(author)
        pdf.set_creator('Nuntiare Report Tollkit - https://formateli.com')
        pdf.set_auto_page_break(False)
        pdf.set_margins(0, 0)

        pdf.add_page()

        pdf.set_xy(0, 0)

        pdf.set_line_width(1)
        pdf.set_draw_color(0, 0, 255)
        pdf.set_fill_color(0, 255, 0)
        pdf.rect(0, 0, 100, 50, 'DF')

        pdf.set_xy(50, 50)

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Welcome to Python!", ln=1)

        pdf.output(self.result_file)

    def help(self):
        'FPdfRender help'
