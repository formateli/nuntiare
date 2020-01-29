# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

"Pluma Highlight test"

from nuntiare.pluma.highlight import Highlight, HighlightBlocks
from nuntiare.pluma.widget import TextEvent
from tkinter import Text, END
import unittest


class HighlightTest(unittest.TestCase):
    def test_highlight(self):
        self.text = TextEvent(None, None, None, is_test=True)
        self.text.bind("<<TextModified>>", self.onTextModified)

        highlight = Highlight()
        highlight.set_syntax(self._get_syntax_python())
        highlight.set_syntax(self._get_syntax_xml())

        self.hl = highlight.get_hl_for_extension('py')
        self.hl_blocks = HighlightBlocks()

        # Document not loaded, so no tags are set.
        # Just one exists: 'sel'
        self.assertEqual(len(self.text.tag_names()), 1)

        # load document
        self.text.insert('1.0', self._get_python_sample_1())

        # Document is loaded, so besides 'sel' tag
        # 'reserved', 'comment' and 'quote' are set.
        self.assertEqual(len(self.text.tag_names()), 4)

        self._ranges = self._get_tag_ranges()
        self._verify_tag('reserved', 'from', '1.4', '1.8')

        # One line 'abc from fgh'
        self.assertEqual(len(self.hl_blocks._lines), 1)

        line = self.hl_blocks.get_line(1)
        # Just one block for 'from' reserved word
        self.assertEqual(len(line), 1)
        l = line[0]
        self.assertEqual(
            (l.line_start, l.col_start, l.line_end, l.col_end),
            (1, 4, 1, 8))

        # Add letter 'd' to non block area
        self.text.insert('1.3', 'd')
        # Remain one line
        self.assertEqual(len(self.hl_blocks._lines), 1)
        line = self.hl_blocks.get_line(1)
        # Remain one block
        self.assertEqual(len(line), 1)
        l = line[0]
        self.assertEqual(
            (l.line_start, l.col_start, l.line_end, l.col_end),
            (1, 5, 1, 9))

        # Break line at position 4
        self.text.insert('1.4', '\n')
        # Two lines now
        self.assertEqual(len(self.hl_blocks._lines), 2)

        # Tags
        self._ranges = self._get_tag_ranges()
        self._verify_tag('reserved', 'from', '2.1', '2.5')

        line = self.hl_blocks.get_line(2)
        self.assertEqual(len(line), 1)
        l = line[0]
        self.assertEqual(
            (l.line_start, l.col_start, l.line_end, l.col_end),
            (2, 1, 2, 5))

        # Insert two lines text
        # ab
        # def xyz
        # pqrcd
        #  from fgh
        self.text.insert('1.2', '\ndef xyz\npqr')
        # four lines now
        self.assertEqual(len(self.hl_blocks._lines), 4)

        # Tags
        self._ranges = self._get_tag_ranges()
        self._verify_tag('reserved', 'def', '2.0', '2.3')

        line = self.hl_blocks.get_line(2)
        self.assertEqual(len(line), 1)
        l = line[0]
        self.assertEqual(
            (l.line_start, l.col_start, l.line_end, l.col_end),
            (2, 0, 2, 3))

        self._verify_tag('reserved', 'from', '4.1', '4.5')
        line = self.hl_blocks.get_line(4)
        self.assertEqual(len(line), 1)
        l = line[0]
        self.assertEqual(
            (l.line_start, l.col_start, l.line_end, l.col_end),
            (4, 1, 4, 5))





        return

        # load document
        self.text.insert('1.0', self._get_python_sample_2())

        # Document is loaded, so besides 'sel' tag
        # 'reserved', 'comment' and 'quote' are set.
        self.assertEqual(len(self.text.tag_names()), 4)

        self._ranges = self._get_tag_ranges()

        self._verify_tag('comment', '# one line comment', '1.0', '1.18')
        self._verify_tag('reserved', 'class', '2.0', '2.5')
        self._verify_tag('reserved', 'def', '3.4', '3.7')
        self._verify_tag('quote', '"#str1"', '4.8', '4.15')
        self._verify_tag('quote', '"#str2"', '4.17', '4.24')
        self._verify_tag('quote', '"str1"', '5.13', '5.19')
        self._verify_tag('quote', '"str2"', '5.22', '5.28')

        # Text widget append a new line at the end
        self.assertEqual(len(self.hl_blocks._lines), 13)

        line = self.hl_blocks.get_line(5)
        self.assertEqual(len(line), 2)

        # Text changed

        # Insert one separator char in a no blocks area
        self.text.insert('5.12', ',')

        line = self.hl_blocks.get_line(5)
        self.assertEqual(len(line), 2)

        self.assertEqual(
            (
                line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end
            ),
            (5, 14, 5, 20)
        )

        self._ranges = self._get_tag_ranges()
        self._verify_tag('comment', '# one line comment', '1.0', '1.18')
        self._verify_tag('reserved', 'class', '2.0', '2.5')
        self._verify_tag('reserved', 'def', '3.4', '3.7')
        self._verify_tag('quote', '"#str1"', '4.8', '4.15')
        self._verify_tag('quote', '"#str2"', '4.17', '4.24')
        self._verify_tag('quote', '"str1"', '5.14', '5.20')
        self._verify_tag('quote', '"str2"', '5.23', '5.29')

        # insert a new line, so all lines below this sums 1
        self.text.insert('3.19', '\n')

        self.assertEqual(len(self.hl_blocks._lines), 14)

        line = self.hl_blocks.get_line(6)
        self.assertEqual(len(line), 2)

        self.assertEqual(
            (
                line[0].line_start, line[0].col_start,
                line[0].line_end, line[0].col_end
            ),
            (6, 14, 6, 20)
        )

    def _verify_tag(self, tag_name, txt, start, end):
        ranges = self._ranges[tag_name]
        range_ok = None
        for r in ranges:
            if r[0] == start and r[1] == end:
                range_ok = True
                break

        if not range_ok:
            raise Exception("Tag '{0}' not in range. '{1}'-'{2}'".format(
                tag_name, start, end))

        self.assertEqual(self.text.get(start, end), txt)

    def _get_tag_ranges(self):
        res = {}
        tags = self.text.tag_names()

        for tag in tags:
            if tag == 'sel':
                continue
            res[tag] = []
            ranges = self.text.tag_ranges(tag)
            i = 0
            while i < len(ranges):                
                res[tag].append(
                        [ranges[i].string, ranges[i + 1].string]
                    )
                i += 2
        #print(res)
        return res

    def onTextModified(self, event):
        text_info = self.text.text_changed_info.copy()
        self.hl.apply_hl(self.text, text_info, self.hl_blocks)

    def _get_python_sample_1(self):
        return '''abc from fgh'''

    def _get_python_sample_2(self):
        return '''# one line comment
class ThisIsAClass():
    def def_test():
        "#str1", "#str2"
        abcd "str1" + "str2"
    """
        Multiline 1
        Multiline 2
        Multiline 3
    """
    def other_function():
        # other comment
        '''

    def _get_syntax_python(self):
        return '''<highlightDefinition caseSensitive="1" extensions="py">
	<styles>
        <style name="reserved" foreColor="blue" backColor="" bold="0" italic="0" />
        <style name="comment" foreColor="green" backColor="" bold="0" italic="0" />
        <style name="quote" foreColor="red" backColor="" bold="0" italic="0" />
	</styles>

	<separators>
		<separator value="." />
		<separator value="," />
		<separator value=":" />
		<separator value="-" />
		<separator value="+" />
		<separator value="=" />
		<separator value="(" />
		<separator value=")" />
		<separator value="[" />
		<separator value="]" />
		<separator value="{" />
		<separator value="}" />
		<separator value=";" />
		<separator value="?" />
	</separators>

	<descriptors>

		<descriptor style="reserved" type="WholeWord" description="Set of words to be highlighted" >
			<tokens>
				<token value="and"/>
				<token value="as"/>
				<token value="assert"/>
				<token value="break"/>-
				<token value="class"/>
				<token value="continue"/>
				<token value="def"/>
				<token value="del"/>
				<token value="elif"/>
				<token value="else"/>
				<token value="except"/>
				<token value="False"/>
				<token value="finally"/>
				<token value="for"/>
				<token value="from"/>
				<token value="global"/>
				<token value="if"/>
				<token value="import"/>
				<token value="in"/>
				<token value="is"/>
				<token value="lambda"/>
				<token value="None"/>
				<token value="nonlocal"/>
				<token value="not"/>
				<token value="or"/>
				<token value="pass"/>
				<token value="raise"/>
				<token value="return"/>
				<token value="True"/>
				<token value="try"/>
				<token value="while"/>
				<token value="with"/>
				<token value="yield"/>
				<token value="self"/>
                <token value="super"/>
			</tokens>
		</descriptor>

		<descriptor style="quote" type="ToCloseToken" multiLine="1" description="Multiline quote">
			<tokens>
				<token value="&quot;&quot;&quot;" closeToken="&quot;&quot;&quot;"/>
			</tokens>
		</descriptor>

		<descriptor style="quote" type="ToCloseToken" description="String between quotes">
			<tokens>
				<token value="&quot;" closeToken="&quot;"/>
			</tokens>
		</descriptor>

		<descriptor style="quote" type="ToCloseToken" description="String between single quotes">
			<tokens>
				<token value="'" closeToken="'"/>
			</tokens>
		</descriptor>

		<descriptor style="comment" type="ToEOL" description="Comment line" >
			<tokens>
				<token value="#"/>
			</tokens>
		</descriptor>

	</descriptors>

</highlightDefinition>
        '''

    def _get_syntax_xml(self):
        return '''<highlightDefinition caseSensitive="0"  extensions="xml,build,page,rdl,rdlc,addin,nuntiare">

	<styles>
		<style name="reserved" foreColor="blue" backColor="" bold="0" italic="0" />
		<style name="comment" foreColor="green" backColor="" bold="0" italic="0" />
		<style name="attr" foreColor="brown" backColor="" bold="0" italic="0" />
		<style name="quote" foreColor="red" backColor="" bold="0" italic="0" />
	</styles>

	<separators>
	</separators>

	<descriptors>
		<descriptor style="reserved" type="ToCloseToken" description="Xml Element">
			<tokens>
				<token value="&lt;" closeToken="&gt;"/>
			</tokens>
            <!-- Sub descriptors -->
	        <descriptors>
                <descriptor style="attr" type="Regex" description="Attribute Name">
                    <tokens>
                        <token value="\s(.*)="/>
                    </tokens>
		        </descriptor>
		        <descriptor style="quote" type="ToCloseToken" description="Attribute value">
			        <tokens>
				        <token value="&quot;" closeToken="&quot;"/>
			        </tokens>
		        </descriptor>
	        </descriptors>
		</descriptor>

		<descriptor style="comment" type="ToCloseToken" multiLine="1" description="Comment block">
			<tokens>
				<token value="&lt;!--" closeToken="--&gt;" />
			</tokens>
		</descriptor>

	</descriptors>

</highlightDefinition>'''
