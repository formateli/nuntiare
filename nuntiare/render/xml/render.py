# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
from xml.dom import minidom
from .. render import Render
from ... import LOGGER


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
                if member.group.sub_group:
                    grp = groups[member.group]
                    grp['children'] = {}
                    for child in member.group.sub_group:
                        grp['children'][child.name] = \
                            {'current_instance': None}

            if member.parent_member:
                if member.parent_member.data_element_output == 'NoOutput':
                    m['data_element_output'] = 'NoOutput'

            if member.children:
                self._get_members(
                    member.children, members_tree, groups)

    def _append_member_group_to_parent(
            self, doc, tablix, row, members_tree, groups,
            tablix_element, member_el):
        parent_group = row.member.get_parent_group(tablix)
        if parent_group:
            pg = groups[parent_group]
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

    def _create_children_groups_el(self, doc, groups, group, group_el):
        grp = groups[group]
        for child in group.sub_group:
            ch_grp = groups[child]
            ch_el = doc.createElement(
                ch_grp['member']['data_element_name'])
            group_el.appendChild(ch_el)
            grp['children'][child.name]['collection_el'] = ch_el
            grp['children'][child.name]['current_instance'] = 'NEW_BLANK'

    def _new_group_instance(
            self, doc, tablix, tablix_element,
            members_tree, groups, group):
        grp = groups[group]
        grp_el = doc.createElement(group.data_element_name)
        grp['element'] = grp_el
        member = grp['member']
        parent_group = member['member'].get_parent_group(tablix)

        if parent_group:
            pg = groups[parent_group]
            member_el = pg['children'][group.name]['collection_el']
        else:
            member_el = self._get_element(
                doc, grp['member'],
                members_tree, tablix_element)
        member_el.appendChild(grp_el)
        grp['current_row_instance'] = 'NEW_BLANK'
        return grp_el

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
                if not row.member:
                    continue
                member = members_tree[row.member]
                if member['data_element_output'] == 'NoOutput':
                    continue
                if row.member.group and \
                        member['group_element_output'] == 'NoOutput':
                    continue

                element = None

                if not member['parent_member'] and \
                        not row.member.group_belongs:
                    element = self._get_element(
                        doc, member, members_tree, tablix_element)

                elif not row.member.group_belongs:
                    element = self._get_element(
                        doc, member, members_tree, tablix_element)

                elif not row.member.group and \
                        row.member.group_belongs:
                    grp = groups[row.member.group_belongs]
                    new_instance = False
                    if (grp['current_row_instance'] in
                            ['NEW_BLANK', row.instance]):
                        grp_el = grp['element']
                    else:
                        new_instance = True
                        grp_el = self._new_group_instance(
                            doc, it, tablix_element, members_tree, groups,
                            row.member.group_belongs)

                    element = doc.createElement(
                        row.member.data_element_name)
                    grp_el.appendChild(element)
                    grp['current_row_instance'] = row.instance
                    if new_instance and row.member.group_belongs.sub_group:
                        self._create_children_groups_el(
                            doc, groups, row.member.group_belongs, grp_el)

                elif row.member.group and \
                        row.member.group.is_detail_group:
                    grp = groups[row.member.group]
                    element = doc.createElement(
                        row.member.group.data_element_name)
                    if row.instance == grp['current_row_instance']:
                        member_el = grp['element_collection']
                    else:
                        parent_group = row.member.get_parent_group(it)
                        if parent_group:
                            pg = groups[parent_group]
                            curr_child_instance = pg['children'][
                                    row.member.group_belongs.name][
                                        'current_instance']
                            if curr_child_instance not in \
                                    ['NEW_BLANK', row.instance]:
                                grp_el = self._new_group_instance(
                                   doc, it, tablix_element,
                                   members_tree, groups,
                                   parent_group)
                                self._create_children_groups_el(
                                    doc, groups,
                                    parent_group,
                                    grp_el)

                            member_el = \
                                pg['children'][
                                    row.member.group_belongs.name][
                                        'collection_el']
                            pg['children'][
                                row.member.group_belongs.name][
                                    'current_instance'] = row.instance
                        else:
                            member_el = doc.createElement(
                                row.member.data_element_name)
                        grp['element_collection'] = member_el
                        grp['current_row_instance'] = row.instance
                        self._append_member_group_to_parent(
                            doc, it, row, members_tree, groups,
                            tablix_element, member_el)
                    member_el.appendChild(element)

                elif row.member.group:
                    grp = groups[row.member.group]
                    element = doc.createElement(
                        row.member.group.data_element_name)
                    if 'element_collection' in grp:
                        member_el = grp['element_collection']
                    else:
                        member_el = doc.createElement(
                            row.member.data_element_name)
                        grp['element_collection'] = member_el
                        self._append_member_group_to_parent(
                            doc, it, row, members_tree, groups,
                            tablix_element, member_el)
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
                        if item.data_element_output == 'ContentsOnly':
                            rec_element = element
                        else:
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
        value = str(item.value) if item.value is not None else ''
        name = item.data_element_name
        if item.data_element_style == 'Attribute':
            element.setAttribute(name, value)
        else:
            txt_element = doc.createElement(name)
            text = doc.createTextNode(value)
            txt_element.appendChild(text)
            element.appendChild(txt_element)

    def _write_to_file(self, doc):
        try:
            f = open(self.result_file, 'wb')
            try:
                res = doc.toprettyxml(indent='  ', encoding='utf-8')
                f.write(res)
            finally:
                f.close()
        except IOError as e:
            LOGGER.error(
                "I/O Error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e),
                True, "IOError")
        except Exception as e:
            LOGGER.error(
                "Unexpected error trying to write to file '{0}'. {1}.".format(
                    self.result_file, e),
                True, "IOError")

    def help(self):
        'XmlRender help'
