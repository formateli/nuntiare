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

        doc = minidom.Document()
        root_element = doc.createElement(
            report.definition.DataElementName)

        self._render_items(
            report.result.body.items.item_list, doc, root_element)

        doc.appendChild(root_element)

        self._write_to_file(doc)

    def _get_element(
            self, doc, member, members_tree, tablix_element):

        if 'element' in member:
            return member['element']

        member['element'] = doc.createElement(
            member['data_element_name'])

        if not member['parent_member']:
            tablix_element.appendChild(member['element'])
        else:
            pm = members_tree[member['parent_member']]
            parent_element = self._get_element(
                doc, pm, members_tree, tablix_element)
            parent_element.appendChild(member['element'])

        return member['element']

    def _get_members(self, members, members_tree, groups):
        for member in members:
            members_tree[member] = {}
            m = members_tree[member]
            m['member'] = member
            m['data_element_name'] = member.data_element_name
            m['data_element_output'] = member.data_element_output
            m['parent_member'] = member.parent_member
            if member.group:
                groups[member.group] = {}
                groups[member.group]['current_row_instance'] = None
                groups[member.group]['member'] = m
                m['group_element_name'] = \
                    member.group_belongs.data_element_name
                m['group_element_output'] = \
                    member.group_belongs.data_element_output

            if member.parent_member:
                pm = members_tree[member.parent_member]
                if member.parent_member.data_element_output == 'NoOutput':
                    m['data_element_output'] = 'NoOutput'

            if member.children:
                self._get_members(
                    member.children, members_tree, groups)

    def _render_items(self, items, doc, parent):
        if not items:
            return

        for it in items:
            if it.type != 'PageTablix':
                continue

            tablix_element = doc.createElement(it.name)
            parent.appendChild(tablix_element)

            members_tree = {}
            groups = {}
            self._get_members(
                it.row_hierarchy.members,
                members_tree, groups)

            for row in it.grid_body.rows:
                member = members_tree[row.member]

                if member['data_element_output'] == 'NoOutput':
                    continue
                if row.member.group and \
                        member['group_element_output'] == 'NoOutput':
                    continue

                element = None
                if not member['parent_member'] and \
                        not row.member.group_belongs:
                    print("NO PANRENT MEMBER")
                    element = self._get_element(
                        doc, member, members_tree, tablix_element)
                elif not row.member.group_belongs:
                    print("NO GROUP_BELONGS")
                    element = self._get_element(
                        doc, member, members_tree, tablix_element)
                elif not row.member.group and \
                        row.member.group_belongs:
                    print("NO GROUP AND GROUP_BELONGS")
                    grp = groups[row.member.group_belongs]
                    if row.row_instance == grp['current_row_instance']:
                        grp_el = grp['element']
                    else:
                        grp_el = doc.createElement(
                            row.member.group_belongs.data_element_name)
                        grp['element'] = grp_el
                        grp['current_row_instance'] = row.row_instance
                        member_el = self._get_element(
                            doc, grp['member'],
                            members_tree, tablix_element)
                        member_el.appendChild(grp_el)

                    element = doc.createElement(
                        row.member.data_element_name)
                        
                    grp_el.appendChild(element)

                elif row.member.group and \
                        row.member.group.is_detail_group:
                    print("DETAIL GROUP")
                    grp = groups[row.member.group]
                    element = doc.createElement(
                        row.member.group.data_element_name)
                    if row.row_instance == grp['current_row_instance']:
                        member_el = grp['element_collection']
                    else:
                        member_el = doc.createElement(
                            row.member.data_element_name)
                        grp['element_collection'] = member_el
                        grp['current_row_instance'] = row.row_instance
                        if row.member.parent_group:
                            pg = groups[row.member.parent_group]
                            pg['element'].appendChild(member_el)
                        else:
                            if not row.member.parent_member:
                                tablix_element.appendChild(member_el)
                            else:
                                pm = self._get_element(
                                    doc, members_tree[
                                        row.member.parent_member
                                    ],
                                    members_tree, tablix_element)
                                pm.appendChild(member_el)
                    member_el.appendChild(element)

                for cell in row.cells:
                    if not cell.object or not cell.object.item_list:
                        continue
                    type_ = cell.object.item_list[0].type
                    if type_ not in ['PageText', 'PageRectangle']:
                        continue
                    item = cell.object.item_list[0]
                    if item.data_element_output == 'NoOutput':
                        continue

                    if type_ == 'PageRectangle':
                        rec_element = doc.createElement(
                            item.data_element_name)
                        element.appendChild(rec_element)
                        if item.items_info and item.items_info.item_list:
                            for it in item.items_info.item_list:
                                if it.type != 'PageText':
                                    continue
                                self._run_textbox(doc, rec_element, it)
                    else:
                        self._run_textbox(doc, element, item)

    def _run_textbox(self, doc, element, item):
        if item.data_element_style == 'Attribute':
            element.setAttribute(
                item.data_element_name, item.value)
        else:
            txt_element = doc.createElement(
                item.data_element_name)
            text = doc.createTextNode(str(item.value))
            txt_element.appendChild(text)
            element.appendChild(txt_element)

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
