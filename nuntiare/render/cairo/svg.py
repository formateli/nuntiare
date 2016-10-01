# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . render import CairoRender


class SvgRender(CairoRender):
    def __init__(self):
        super(SvgRender, self).__init__(extension='svg')
