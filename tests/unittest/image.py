# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import unittest
from nuntiare.definition.element import EmbeddedImages, EmbeddedImage
from nuntiare.report import Report


class ImageTest(unittest.TestCase):
    def testImageElement(self):
        string_xml = r"""
            <Nuntiare>
              <Name>Size functions Test</Name>
              <Page/>
              <Body>
                <ReportItems>
                  <Image>
                    <Name>fitproportional_1</Name>
                    <ImageSource>Embedded</ImageSource>
                    <MIMEType>image/png</MIMEType>
                    <ImageSizing>FitProportional</ImageSizing>
                    <Value>img-100x50</Value>
                    <Width>15cm</Width>
                    <Height>5cm</Height>
                  </Image>
                </ReportItems>
              </Body>
              <EmbeddedImages>
                <EmbeddedImage>
                  <Name>img-50x100</Name>
                  <MIMEType>image/png</MIMEType>
                  <ImageData>iVBORw0KGgoAAAANSUhEUgAAADIAAABkCAYAAADE6GNbAAAAjElEQVR4nO3PgQkAIRDAsPP331mXED5IM0G7ZmbPA76/A25pRNOIphFNI5pGNI1oGtE0omlE04imEU0jmkY0jWga0TSiaUTTiKYRTSOaRjSNaBrRNKJpRNOIphFNI5pGNI1oGtE0omlE04imEU0jmkY0jWga0TSiaUTTiKYRTSOaRjSNaBrRNKJpRHMAMfcBx4WqLOwAAAAASUVORK5CYII=</ImageData>
                </EmbeddedImage>
                <EmbeddedImage>
                  <Name>img-100x50</Name>
                  <MIMEType>image/png</MIMEType>
                  <ImageData>iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAAAj0lEQVR4nO3RQQ0AIBDAsAP/nuGNAvZoFSzZmpkzZOzfAbwMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2IMiTEkxpAYQ2Iun3sBY2CRYj8AAAAASUVORK5CYII=</ImageData>
                </EmbeddedImage>
              </EmbeddedImages>
            </Nuntiare>"""

        report = Report(string_xml)
        report.run()

        self.assertEqual(
            len(report.definition.EmbeddedImages.embedded_images), 2)

    def testImageFunctions(self):
        width, height = EmbeddedImage.get_proportional_size(
            container_width=100,
            container_height=50,
            image_width=10,
            image_height=5)
        self.assertEqual(width, 100)
        self.assertEqual(height, 50)
