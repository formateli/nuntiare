# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk
from .image import ImageManager


class Theme(ttk.Style):

    _themes = {}
    _curr_theme = None
    _bind_callbacks = {'theme_changed': []}
    _images = ImageManager()
    _xml_theme_folder = None

    @classmethod
    def set_theme(cls, name):
        if cls._curr_theme and cls._curr_theme.name == name:
            return

        if name is None:
            cls._curr_theme = None
            cls._fire_event('theme_changed')
            return

        style = ttk.Style()

        if name in style.theme_names():
            style.theme_use(name)
            if name in cls._themes:
                cls._curr_theme = cls._themes[name]
            else:
                cls._curr_theme = None
            cls._fire_event('theme_changed')
            return

        # Theme are lazy loaded

        xml_theme_config = cls._get_theme_from_xml(name)
        if xml_theme_config is not None:
            config = xml_theme_config
        else:
            config = cls._get_default_config()

        theme = _Theme(name, config, style)
        cls._themes[name] = theme
        cls._curr_theme = theme
        cls._fire_event('theme_changed')

    @classmethod
    def bind(cls, event, callback):
        if not event in cls._bind_callbacks:
            raise Exception(
                "Invalid bind event '{}' for Theme.".format(event))
        cls._bind_callbacks[event].append(callback)

    @classmethod
    def _fire_event(cls, event):
        callbacks = cls._bind_callbacks[event]
        for c in callbacks:
            c(cls._curr_theme)

    @classmethod
    def _get_theme_from_xml(cls, name):
        if cls._xml_theme_folder is None:
            dir_ = os.path.dirname(os.path.realpath(__file__))
            dir_ = os.path.normpath(os.path.join(dir_, 'themes'))
            cls._xml_theme_folder = dir_

        file_ = os.path.join(cls._xml_theme_folder, name + '.xml')
        if not os.path.exists(file_):
            #TODO loggin
            print("Material theme '{}' does not exist. Loading default.".format(name))
            return

        config = None
        try:
            root = ET.parse(file_).getroot()
            config = cls._get_theme_config(root)
        except ET.ParseError as e:
            print("Error parsing xml Material theme '{}'. {}".format(name, e))
            return

        return config

    @classmethod
    def _get_theme_config(cls, root):
        config = cls._get_default_config().copy()
        for child in root:
            tag = child.tag.lower()
            if tag in ['name', 'description']:
                pass
            elif tag == 'primarycolor':
                config['primary_color'] = child.text
            elif tag == 'primaryvariantcolor':
                config['primary_variant_color'] = child.text
            elif tag == 'secondarycolor':
                config['secondary_color'] = child.text
            elif tag == 'secondaryvariantcolor':
                config['secondary_variant_color'] = child.text
            elif tag == 'backgroundcolor':
                config['background_color'] = child.text
            elif tag == 'surfacecolor':
                config['surface_color'] = child.text
            elif tag == 'errorcolor':
                config['error_color'] = child.text
            elif tag == 'primarytextcolor':
                config['primary_text_color'] = child.text
            elif tag == 'secondarytextcolor':
                config['secondary_text_color'] = child.text
            elif tag == 'backgroundtextcolor':
                config['background_text_color'] = child.text
            elif tag == 'surfacetextcolor':
                config['surface_text_color'] = child.text
            elif tag == 'errortextcolor':
                config['error_text_color'] = child.text
            elif tag == 'font':
                config['font'] = child.text
            else:
                print("Unknown option theme '{}'.".format(tag))
        return config


    @classmethod
    def _get_default_config(cls):
        # see https://material.io/design/color/the-color-system.html#color-theme-creation
        default = {
            # A primary color is the color displayed most
            # frequently across your app’s screens and components.
            'primary_color':            '#6200EE',
            'primary_variant_color':    '#3700B3',
            # Secondary colors are best for:
            #  - Floating action buttons
            #  - Selection controls, like sliders and switches
            #  - Highlighting selected text
            #  - Progress bars
            #  - Links and headlines
            'secondary_color':          '#03DAC6',
            'secondary_variant_color':  '#018786',
            # The background color appears behind scrollable content
            'background_color':         '#d9d9d9',
            # Surface colors affect surfaces of components,
            # such as cards, sheets, and menus.
            'surface_color':            '#FFFFFF',
            # Error color indicates errors in components
            'error_color':              '#B00020',
            'primary_text_color':       '#FFFFFF',
            'secondary_text_color':     '#000000',
            'background_text_color':    '#000000',
            'surface_text_color':       '#000000',
            'error_text_color':         '#FFFFFF',
            'font':                     'Helvetica 10',
            'disabled_color':           '#cccccc',
        }
        return default


class _Theme:
    def __init__(self, name, config, style):
        self.name = name
        self.config = config
        self._create_theme(style)

    def _create_theme(self, style):
        images = Theme._images

        style.theme_create(self.name, parent='clam')
        style.theme_use(self.name)

        config = self.config

        style.configure(
                ".",
                background=config['surface_color'],
                foreground=config['surface_text_color'],
                **config
            )

        style.configure(
                "GroupToolBar.TFrame",
                background=config['primary_color'],
                foreground=config['primary_text_color'],
            )

        style.configure(
                "GroupToolBar.TButton",
                background=config['primary_color'],
                foreground=config['primary_text_color'],
            )

        style.configure(
                "OnOffButton",
                oncolor=config['primary_color'],
                offcolor=config['secondary_text_color'],
            )

        ## Scrollbars
        style.layout('Vertical.TScrollbar', [
                ('Vertical.Scrollbar.trough', {'sticky': 'ns', 'children': [
                    ('Vertical.Scrollbar.thumb', {'expand': 'true'})
                ]
                })
            ])

        style.layout('Horizontal.TScrollbar', [
                ('Horizontal.Scrollbar.trough', {'sticky': 'ew', 'children': [
                    ('Horizontal.Scrollbar.thumb', {'expand': 'true'})
                ]
                })
            ])

        style.element_create(
                'Horizontal.Scrollbar.trough',
                'image',
               images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['background_color'], size='24x2'),
                ('disabled', images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['disabled_color'], size='24x2')),
                #border=(6, 0, 6, 0),
                border=0,
                sticky='ew'
            )

        style.element_create(
                'Horizontal.Scrollbar.thumb',
                'image',
               images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['primary_color']),
                ('pressed', '!disabled', images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['secondary_color'])),
                ('active', '!disabled', images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['disabled_color'])),
                #border=(6, 0, 6, 0),
                border=0,
                sticky='ew'
            )

        style.element_create(
                'Vertical.Scrollbar.trough',
                'image',
               images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['background_color'], size='2x24'),
                ('disabled', images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['disabled_color'], size='2x24')),
                #border=(0, 6, 0, 6),
                border=0,
                sticky='ns'
            )

        style.element_create(
                'Vertical.Scrollbar.thumb',
                'image',
               images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['primary_color']),
                ('pressed', '!disabled', images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['secondary_color'])),
                ('active', '!disabled', images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['disabled_color'])),
                #border=(0, 6, 0, 6),
                border=0,
                sticky='ns'
            )


        ## Scales
        style.element_create(
                'Horizontal.Scale.slider',
                'image',
                images.get_image(
                    'scale-slider', size='12x12',
                    color=config['primary_variant_color']),
                ('pressed', '!disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['secondary_color'])),
                ('active', '!disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['disabled_color'])),
                sticky=(),
            )

        style.element_create(
                'Horizontal.Scale.trough',
                'image',
               images.get_image(
                    'scale-trough-horizontal',
                    color=config['primary_variant_color']),
                ('active', '!disabled', images.get_image(
                    'scale-trough-horizontal',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scale-trough-horizontal',
                    color=config['disabled_color'])),
                border=(8, 5, 8, 5),
                sticky='ew',
                padding=0
            )

        style.element_create(
                'Vertical.Scale.slider',
                'image',
                images.get_image(
                    'scale-slider', size='12x12',
                    color=config['primary_variant_color']),
                ('pressed', '!disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['secondary_color'])),
                ('active', '!disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scale-slider', size='12x12',
                    color=config['disabled_color'])),
                sticky=(),
            )

        style.element_create(
                'Vertical.Scale.trough',
                'image',
               images.get_image(
                    'scale-trough-vertical',
                    color=config['primary_variant_color']),
                ('active', '!disabled', images.get_image(
                    'scale-trough-vertical',
                    color=config['secondary_variant_color'])),
                ('disabled', images.get_image(
                    'scale-trough-vertical',
                    color=config['disabled_color'])),
                border=(8, 5, 8, 5),
                sticky='ns',
                padding=0
            )

        # Progressbar

        style.element_create(
                'Horizontal.Progressbar.trough',
                'image',
               images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['background_color']),
                sticky='ew',
            )

        style.element_create(
                'Horizontal.Progressbar.pbar',
                'image',
               images.get_image(
                    'scrollbar-trough-horizontal',
                    color=config['primary_color']),
                sticky='ew',
            )

        style.element_create(
               'Vertical.Progressbar.trough',
                'image',
               images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['background_color']),
                sticky='ns',
            )

        style.element_create(
                'Vertical.Progressbar.pbar',
                'image',
               images.get_image(
                    'scrollbar-trough-vertical',
                    color=config['primary_color']),
                sticky='ns',
            )
