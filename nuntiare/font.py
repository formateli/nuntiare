# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

class NuntiareFont(object):

    @staticmethod
    def get_description():
        return 'Nuntiare default Font Manager'

    @staticmethod
    def get_text_height(text, page, cur_height, style):
        return cur_height - style.padding_top - style.padding_bottom
