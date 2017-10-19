# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

import sys
from xml.dom import minidom
from .. render import Render
from ... import LOGGER

__all__ = ['XmlRender']


class XmlRender(Render):
    def __init__(self):
        super(XmlRender, self).__init__(extension='xml')        

    def render(self, report, overwrite):
        super(XmlRender, self).render(report, overwrite)

        # Attribute or Element. Default Attribute
        default_style = report.definition.DataElementStyle

        doc = minidom.Document()
        root_element = doc.createElement(
            report.definition.DataElementName)

        self._render_items(
            report.result.body.items.item_list, doc, root_element)

        doc.appendChild(root_element)

        self._write_to_file(doc)

    def _render_items(self, items, doc, parent):
        if not items:
            return
        for it in items:
            if it.type != 'PageTablix':
                continue            
            tablix_element = doc.createElement(it.name)
            parent.appendChild(tablix_element)
            self._get_members(
                it.column_hierarchy.members, doc, tablix_element)

    def _get_members(self, members, doc, parent):
        for member in members:
            member_element = doc.createElement(
                member.data_element_name)
            parent.appendChild(member_element)
            if member.group:
                self._get_groups(member.group, doc, member_element)
            if member.children:
                self._get_members(member.children, doc, member_element)

    def _get_groups(self, group, doc, parent):
        group_element = doc.createElement(group.data_element_name)
        parent.appendChild(group_element)

    def _write_to_file(self, doc):
        try:
            f = open(self.result_file, 'wb')
            try:
                f.write(
                    doc.toprettyxml(indent='  ', encoding='utf-8'))
            finally:
                f.close()
        except IOError as e:
            LOGGER.error(
                "I/O Error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e.strerror),
                True, "IOError")
        except:
            LOGGER.error(
                "Unexpected error trying to write to file '{0}'. {1}.".format(
                    self.result_file, sys.exc_info()[0]),
                True, "IOError")

    def help(self):
        'XmlRender help'
