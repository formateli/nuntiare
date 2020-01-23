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

        self.hl = highlight.get_hl_for_extension('py')
        self.hl_blocks = HighlightBlocks()

        # Document not loaded, so no tags are set.
        # Just one exists: 'sel'
        self.assertEqual(len(self.text.tag_names()), 1)

        # load document
        self.text.insert('1.0', self._get_python_sample())

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

    def _get_python_sample(self):
        return '''# one line comment
class ThisIsAClass():
    def def_test():
        "#str1", "#str2"
        abcd "str1" + "str2"
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
