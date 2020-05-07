# This file is part of Nuntiare project.
# The COYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import unittest
from tools import get_report_path
from nuntiare.report import Report
from nuntiare.render.cairo.pdf import PdfRender


class RenderPdfTest(unittest.TestCase):
    def test_Colums(self):
        report_str = r'''
<Nuntiare>
  <Name>Pdf Column Test</Name>
  <Page>
    <PageWidth>100</PageWidth>
    <PageHeight>200</PageHeight>
    <BottomMargin>5</BottomMargin>
    <RightMargin>5</RightMargin>
    <TopMargin>5</TopMargin>
    <LeftMargin>5</LeftMargin>
    <Columns>{0}</Columns>
  </Page>
  <Body>
    <ReportItems>
      <Line>
        <Name>LineTest</Name>
        <Top>1</Top>
        <Left>1</Left>
        <Height>0</Height>
        <Width>2</Width>
      </Line>
      <Line>
        <Name>LineTest2</Name>
        <Top>191</Top>
        <Left>1</Left>
        <Height>0</Height>
        <Width>2</Width>
      </Line>
    </ReportItems>
  </Body>
</Nuntiare>
'''
        pdf = PdfRender()
        limit = 5
        i = 1
        while i <= limit:
            rstr = report_str.format(i)
            report = Report(rstr)
            report.run()
            result = report.result
            self.assertEqual(result.columns, i)
            pdf.render(report, overwrite=True)
            pages = pdf.pages
            frames = pages.frames
            # available height
            self.assertEqual(frames.height, 190)
            if i == 1:
                # Second Line item is located on
                # second page
                self.assertEqual(len(pages.pages), 2)
                # Two frames, one per page
                self.assertEqual(len(frames.frames), 2)
            else:
                # When columns > 1 second Line item moves
                # to next frame in same page
                self.assertEqual(len(pages.pages), 1)
                self.assertEqual(len(frames.frames), i)
            heigth_sum = 0.0
            for f in frames.frames:
                self.assertEqual(f.top, heigth_sum)
                self.assertEqual(f.bottom, heigth_sum + frames.height)
                heigth_sum += frames.height
            i += 1

    def test_keeptogether_1(self):
        report = Report(get_report_path('keep_together_1.xml'))
        report.run()

        pdf = PdfRender()
        pdf.render(report, overwrite=True)

        pages = pdf.pages
        frames = pdf.pages.frames

        # Total pages
        self.assertEqual(len(pages.pages), 3)
        # Total frames
        self.assertEqual(len(frames.frames), 3)

        cairo_items = frames.frames[0].cairo_items
        self.assertEqual(len(cairo_items), 4)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 40.0, 5.0)
        self._verify_item(
            'Rectangle_3', cairo_items[1], 40.0, 75.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 40.0, 110.0)
        self._verify_item(
            'Rectangle_5', cairo_items[3], 40.0, 145.0)

        cairo_items = frames.frames[1].cairo_items
        self.assertEqual(len(cairo_items), 10)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 90.0, 5.0, 50.0)
        self._verify_item(
            'Rectangle_1_b', cairo_items[1], 115.0, 5.0)
        self._verify_item(
            'Rectangle_2', cairo_items[2], 90.0, 40.0)
        self._verify_item(
            'Rectangle_2_b', cairo_items[3], 165.0, 40.0)
        self._verify_item(
            'Rectangle_3', cairo_items[4], 90.0, 75.0, 50)
        self._verify_item(
            'Rectangle_4', cairo_items[5], 90.0, 110.0, 50)
        self._verify_item(
            'Rectangle_5', cairo_items[6], 90.0, 145.0, 50)
        self._verify_item(
            'Rectangle_5_b', cairo_items[7], 115.0, 145.0)
        self._verify_item(
            'Rectangle_6', cairo_items[8], 90.0, 180.0)
        self._verify_item(
            'Rectangle_6_b', cairo_items[9], 165.0, 180.0)

        cairo_items = frames.frames[2].cairo_items
        self.assertEqual(len(cairo_items), 4)
        self._verify_item(
            'Rectangle_3', cairo_items[0], 180.0, 75.0, 140)
        self._verify_item(
            'Rectangle_3_b', cairo_items[1], 205.0, 75.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 180.0, 110.0, 140)
        self._verify_item(
            'Rectangle_4_b', cairo_items[3], 205.0, 110.0)

    def test_keeptogether_2(self):
        report = Report(get_report_path('keep_together_2.xml'))
        report.run()

        pdf = PdfRender()
        pdf.render(report, overwrite=True)

        pages = pdf.pages
        frames = pdf.pages.frames

        # Total pages
        self.assertEqual(len(pages.pages), 3)
        # Total frames
        self.assertEqual(len(frames.frames), 3)

        cairo_items = frames.frames[0].cairo_items
        self.assertEqual(len(cairo_items), 4)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 5.0, 40.0)
        self._verify_item(
            'Rectangle_3', cairo_items[1], 75.0, 40.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 110.0, 40.0)
        self._verify_item(
            'Rectangle_5', cairo_items[3], 145.0, 40.0)

        cairo_items = frames.frames[1].cairo_items
        self.assertEqual(len(cairo_items), 10)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 220, 0.0, x_minus=50.0)
        self._verify_item(
            'Rectangle_1_b', cairo_items[1], 220.0, 25.0)
        self._verify_item(
            'Rectangle_2', cairo_items[2], 255.0, 0.0)
        self._verify_item(
            'Rectangle_2_b', cairo_items[3], 255.0, 75.0)
        self._verify_item(
            'Rectangle_3', cairo_items[4], 290.0, 0.0, x_minus=50.0)
        self._verify_item(
            'Rectangle_4', cairo_items[5], 325.0, 0.0, x_minus=50.0)
        self._verify_item(
            'Rectangle_5', cairo_items[6], 360.0, 0.0, x_minus=50.0)
        self._verify_item(
            'Rectangle_5_b', cairo_items[7], 360.0, 25.0)
        self._verify_item(
            'Rectangle_6', cairo_items[8], 395.0, 0.0)
        self._verify_item(
            'Rectangle_6_b', cairo_items[9], 395.0, 75.0)

        cairo_items = frames.frames[2].cairo_items
        self.assertEqual(len(cairo_items), 4)
        self._verify_item(
            'Rectangle_3', cairo_items[0], 505.0, 0.0, x_minus=140.0)
        self._verify_item(
            'Rectangle_3_b', cairo_items[1], 505.0, 25.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 540.0, 0.0, x_minus=140.0)
        self._verify_item(
            'Rectangle_4_b', cairo_items[3], 540.0, 25.0)

    def test_keeptogether_3(self):
        report = Report(get_report_path('keep_together_3.xml'))
        report.run()

        pdf = PdfRender()
        pdf.render(report, overwrite=True)

        pages = pdf.pages
        frames = pdf.pages.frames

        # Total pages
        self.assertEqual(len(pages.pages), 5)
        # Total frames
        self.assertEqual(len(frames.frames), 5)

        cairo_items = frames.frames[0].cairo_items
        self.assertEqual(len(cairo_items), 6)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 40.0, 5.0)
        self._verify_item(
            'Rectangle_3', cairo_items[1], 40.0, 75.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 40.0, 110.0)
        self._verify_item(
            'Rectangle_5', cairo_items[3], 40.0, 145.0)
        self._verify_item(
            'Rectangle_7', cairo_items[4], 10.0, 215.0)
        self._verify_item(
            'Rectangle_9', cairo_items[5], 80.0, 215.0)

        # Second page, where items 7 and 8 are extended.
        cairo_items = frames.frames[1].cairo_items
        self.assertEqual(len(cairo_items), 2)
        self._verify_item(
            'Rectangle_7', cairo_items[0], 100, 0.0, x_minus=35.0)
        self._verify_item(
            'Rectangle_8', cairo_items[1], 125, 0.0)

        # Third page, just item 7 (final part is extended)
        cairo_items = frames.frames[2].cairo_items
        self.assertEqual(len(cairo_items), 1)
        self._verify_item(
            'Rectangle_7', cairo_items[0], 190, 0.0, x_minus=285.0)

        cairo_items = frames.frames[3].cairo_items
        self.assertEqual(len(cairo_items), 12)
        self._verify_item(
            'Rectangle_1', cairo_items[0], 270, 5.0, y_minus=50.0)
        self._verify_item(
            'Rectangle_1_b', cairo_items[1], 295.0, 5.0)
        self._verify_item(
            'Rectangle_2', cairo_items[2], 270.0, 40.0)
        self._verify_item(
            'Rectangle_2_b', cairo_items[3], 345.0, 40.0)
        self._verify_item(
            'Rectangle_3', cairo_items[4], 270.0, 75.0, y_minus=50.0)
        self._verify_item(
            'Rectangle_4', cairo_items[5], 270.0, 110.0, y_minus=50.0)
        self._verify_item(
            'Rectangle_5', cairo_items[6], 270.0, 145.0, y_minus=50.0)
        self._verify_item(
            'Rectangle_5_b', cairo_items[7], 295.0, 145.0)
        self._verify_item(
            'Rectangle_6', cairo_items[8], 270.0, 180.0)
        self._verify_item(
            'Rectangle_6_b', cairo_items[9], 345.0, 180.0)

        cairo_items = frames.frames[4].cairo_items
        self.assertEqual(len(cairo_items), 4)
        self._verify_item(
            'Rectangle_3', cairo_items[0], 360.0, 75.0, y_minus=140.0)
        self._verify_item(
            'Rectangle_3_b', cairo_items[1], 385.0, 75.0)
        self._verify_item(
            'Rectangle_4', cairo_items[2], 360.0, 110.0, y_minus=140.0)
        self._verify_item(
            'Rectangle_4_b', cairo_items[3], 385.0, 110.0)

    def _verify_item(self, name, item, top, left, y_minus=0.0, x_minus=0.0):
        self.assertEqual(item.item.name, name)
        self.assertEqual(item.top, top)
        self.assertEqual(item.left, left)
        # y_minus and x_minus indicate points to be moved to up
        # or to left in order to clip the item in the frame
        self.assertEqual(item.y_minus, y_minus)
        self.assertEqual(item.x_minus, x_minus)
