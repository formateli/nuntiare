# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from . cairo_item import CairoItem
from ... import LOGGER


class Pages(object):
    class _Page(object):
        def __init__(
                self, body_top, width, header, footer, frames):
            self.body_top = body_top
            self.available_width = width
            self.header = None
            self.footer = None
            if header:
                self.header = Pages._HeaderFooter(
                    self, header)
            if footer:
                self.footer = Pages._HeaderFooter(
                    self, footer)
            self.frames = frames.new_frames(self)
            self.report_items = []

        def add_item(self, it):
            if not it or it.type != 'PageText':
                return
            self.report_items.append(it)


    class _HeaderFooter(object):
        def __init__(self, page, definition):
            self.top = 0.0
            self.height = definition.height
            self.drawable_width = page.available_width
            self.page = page
            self.definition = definition
            self.items = []
            self.cairo_items = []

        def run(self):
            if not self.definition:
                return
            self.definition.run_items()
            cairo_items = Pages._get_cairo_items(
                self.definition.items.item_list)
            for ci in cairo_items:
                Pages._record_item(
                    ci, self, self.top)

        def add_item(self, cairo_item):
            self.items.append(cairo_item.item)
            self.cairo_items.append(cairo_item)
            self.page.add_item(cairo_item.item)


    class _Frames(object):
        class _Frame(object):
            def __init__(
                    self, page, top, height,
                    left, drawable_width):
                self.page = page
                self.top = top
                self.height = height
                self.bottom = top + height
                self.left = left
                self.drawable_width = drawable_width
                self.items = []
                self.cairo_items = []
                # True if this frame is an extension
                # for items that exceeds previous frame width.
                self.horizontal_extention = False

            def in_limits(self, top_ref):
                if top_ref >= self.top and \
                        top_ref < self.bottom:
                    return True

            def add_item(self, cairo_item):
                self.items.append(cairo_item.item)
                self.cairo_items.append(cairo_item)
                self.page.add_item(cairo_item.item)

        def __init__(
                self, width, height,
                columns, column_space):
            self.columns = columns
            self.column_space = column_space
            self.height = height
            self.frames = []

            total_space = 0.0
            if self.columns > 1:
                total_space = self.column_space * (self.columns - 1)
            self.drawable_width = (width - total_space) / self.columns

        def is_last_frame(self, frame):
            last_frame = self.frames[len(self.frames) - 1]
            return frame == last_frame

        def get_frame_index(self, frame):
            i = 0
            for f in self.frames:
                if f == frame:
                    return i
                i += 1

        def new_frames(self, page):
            result = []
            top = page.body_top
            i = 0
            while i < self.columns:
                left = self.drawable_width * i
                left += (self.column_space * i)
                fr = Pages._Frames._Frame(
                    page, top, self.height,
                    left, self.drawable_width)
                result.append(fr)
                top += self.height
                i += 1
            self.frames.extend(result)
            return result

        def get_frame(self, top_ref):
            for frame in self.frames:
                if frame.in_limits(top_ref):
                    return frame

        def lenght(self):
            return self.height * self.columns

    def __init__(self, report):
        self.report = report
        self.pages = []

        result = report.result

        self.frames = Pages._Frames(
            result.available_width,
            result.body.available_height,
            result.columns,
            result.column_spacing)
        self._make_pages()

    def _make_pages(self):
        result = self.report.result
        cairo_items = self._get_cairo_items(
            result.body.items.item_list)

        if cairo_items:
            completed = False
            while not completed:
                curr_index = 0
                for ci in cairo_items:
                    if not ci.placed:
                        status = 1
                        while status == 1:
                            # Item is moved to next frame/page
                            status = self._set_page(
                                ci, cairo_items, curr_index)
                        if status == 2:
                            # Process all items again.
                            # probably bacause new item(s) addition.
                            break
                    curr_index += 1
                    if curr_index == len(cairo_items):
                        completed = True
                        break

        if not self.pages:
            return

        if not result.header and not result.footer:
            return

        self.report.globals['PageNumber'] = 1
        self.report.globals['TotalPages'] = len(self.pages)
        is_first_page = True
        is_last_page = False
        for page in self.pages:
            if self.report.globals['PageNumber'] == \
                    len(self.pages):
                is_last_page = True
            self._set_header_footer(
                result.header, page.header,
                is_first_page, is_last_page)
            self._set_header_footer(
                result.footer, page.footer,
                is_first_page, is_last_page)
            self.report.globals['PageNumber'] += 1
            is_first_page = False

    def _new_page(self):
        result = self.report.result
        i = len(self.pages)
        if i == 0:
            top = 0.0
        else:
            pg = self.pages[i - 1]
            top = pg.body_top + self.frames.lenght()
        pg = Pages._Page(
            top,
            result.available_width,
            result.header,
            result.footer,
            self.frames)
        self.pages.append(pg)

    def _set_page(self, ci, cairo_items, curr_index):
        '''
        Return:
        0: Item placed
        1: Item moved to next frame/page
            and must be processed again
        2: New item(s) added because current item
            is clipped in two or more frames/pages
        '''
        frame = None
        while frame is None:
            # Get the probably frame for this ci.
            # New frames are created as needed.
            frame = self._get_frame(ci)
            if not frame:
                continue

            if ci.horizontal_extention:
                if frame.horizontal_extention:
                    # already in correct frame
                    continue
                frame.horizontal_extention = True
                if self.frames.is_last_frame(frame) and \
                        len(frame.cairo_items) == 0:
                    # Continue normally
                    continue
                # Move all placed ci one frame down
                # and process all again
                idx = self.frames.get_frame_index(frame)
                while idx < len(self.frames.frames):
                    for c in self.frames.frames[idx].cairo_items:
                        c.top += self.frames.height
                        c.placed = False
                    self.frames.frames[idx].cairo_items = []
                    idx += 1
                return 2

            if frame.horizontal_extention and \
                    not ci.left + ci.width > self.frames.drawable_width:
                # frame already contains horizontal extended items.
                # This ci is not supposed to be an horizontal extended item,
                # so move it to next frame
                ci.top += self.frames.height
                return 1

        if ci.checked:
            self._record_item(
                ci, frame, frame.top)
            return 0

        exceeds_v = ci.top + ci.height > frame.bottom
        exceeds_h = ci.left + ci.width > self.frames.drawable_width

        if exceeds_v:
            page_count, start_diff = self._get_pages_down(
                ci, self.frames.height, frame.bottom)

            ci.checked = True
            if page_count == 1:
                ci.top += start_diff
                self._push_peers('down', ci, cairo_items, start_diff)
                return 1
            else:
                y_minus = start_diff
                x = 1
                while x < page_count:
                    new_ci = ci.clone()
                    new_ci.top = frame.top + (frame.height * x)
                    new_ci.checked = True
                    new_ci.y_minus = y_minus
                    cairo_items.insert(curr_index + x, new_ci)
                    y_minus += self.frames.height
                    x += 1
                return 2

        elif exceeds_h:
            left_count, page_count, normal_left, space_moved = \
                self._get_pages_extended(ci, self.frames.drawable_width)

            ci.left = normal_left
            ci.checked = True

            if left_count > 1:
                ci.top += self.frames.height * (left_count - 1)

            if page_count == 1:
                ci.horizontal_extention = True
                self._push_peers('right', ci, cairo_items, space_moved)
                return 1
            else:
                x_minus = self.frames.drawable_width - normal_left
                x = 1
                while x < page_count:
                    new_ci = ci.clone()
                    new_ci.top += self.frames.height * x
                    new_ci.left = 0.0
                    new_ci.horizontal_extention = True
                    new_ci.checked = True
                    new_ci.x_minus = x_minus
                    cairo_items.insert(curr_index + x, new_ci)
                    x_minus += self.frames.drawable_width
                    x += 1
                return 2
        else:
            self._record_item(
                ci, frame, frame.top)
            return 0

    def _set_header_footer(
            self, definition, header_footer,
            is_first_page, is_last_page):
        if not definition:
            return
        if not definition.print_on_first_page \
                and is_first_page:
            return
        if not definition.print_on_last_page \
                and is_last_page:
            return
        header_footer.run()

    def _get_frame(self, it):
        frame = self.frames.get_frame(it.top)
        if frame:
            return frame
        self._new_page()

    def _get_pages_down(self, ci, height, bottom):
        # Returns:
        # page_count: Quantity of spread frames
        # start_diff: ci height offset
        start_diff = bottom - ci.top
        if ci.height <= height and ci.item.keep_together:
            # Move to next frame
            return 1, start_diff

        height_diff = ci.height - start_diff
        page_count = self._get_offset_count(height_diff, height)
        return page_count + 1, start_diff

    def _get_pages_extended(self, ci, drawable_width):
        # Returns:
        # left_count: Frame number where ci starts to render
        # frame_count: Quantity of frame needed to render the ci.
        #   1 means that ci fit in one frame.
        # normal_left: Calculated Left for starting frame.
        # space_moved: If ci is move. Ex KeepTogether

        left_count = self._get_offset_count(ci.left, drawable_width)
        normal_left = ci.left - (drawable_width * (left_count - 1))

        if ci.width <= drawable_width:
            if normal_left + ci.width <= drawable_width:
                return left_count, 1, normal_left, 0.0
            elif ci.item.keep_together:
                # Move to next frame
                return left_count + 1, 1, 0.0, drawable_width - normal_left

        width_offset = ci.width - (drawable_width - normal_left)
        page_count = self._get_offset_count(width_offset, drawable_width)

        return left_count, page_count + left_count, normal_left, 0.0

    def _get_offset_count(self, reference, size):
        i = 1
        while True:
            diff = reference / (size * i)
            if diff < 1:
                return i
            i += 1

    @staticmethod
    def _get_cairo_items(items):
        cis = []
        for it in items:
            ci = CairoItem(it)
            cis.append(ci)
        return cis

    @staticmethod
    def _push_peers(direction, it, cairo_items, space_to_move):
        if space_to_move == 0.0:
            return
        for ci in cairo_items:
            if it == ci:
                continue
            if direction == 'down':
                in_zone = it.item.in_zone_down_x(it, ci)
            else:
                in_zone = it.item.in_zone_right(it, ci)
            if in_zone:
                if direction == 'down':
                    ci.top += space_to_move
                else:
                    ci.left += space_to_move

    @staticmethod
    def _record_item(
            ci, section, section_top):
        ci.section_top = section_top
        ci.placed = True
        section.add_item(ci)
