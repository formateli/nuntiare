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

        self.text.insert('1.0', self._get_python_sample())


    def onTextModified(self, event):
        text_info = self.text.text_changed_info.copy()
        self.hl.apply_hl(self.text, text_info, self.hl_blocks)

    def _get_python_sample(self):
        return '''
class ThisIsAClass():
        '''

    def _get_syntax_python(self):
        return '''<highlightDefinition caseSensitive="1" extensions="py">
	<styles>
        <style name="reserved" foreColor="blue" backColor="" bold="0" italic="0" />
        <style name="comment" foreColor="green" backColor="" bold="0" italic="0" />
        <style name="quote" foreColor="red" backColor="" bold="0" italic="0" />
	</styles>

    <!--TODO: data types, Built in Functions, colorize after def and class -->

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


