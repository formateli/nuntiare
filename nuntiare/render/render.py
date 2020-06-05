# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import os
from importlib import import_module
from .. import CONFIG, LOGGER


class Render(object):
    def __init__(self, extension=None):
        self.extension = extension
        self.result_file = None
        self.report = None

    def render(self, report, **kws):
        if not report.result:
            LOGGER.critical(
                'No Result object in report. Have you executed run()?', True)

        self.report = report

        if kws is not None:
            overwrite = kws.get('overwrite', True)

        if self.extension:
            self.result_file = os.path.join(
                report.globals['OutputDirectory'],
                report.globals['OutputName'] + "." + self.extension)
            if not overwrite:
                if os.path.isfile(self.result_file):
                    LOGGER.error(
                        "File '{0}' already exists.".format(self.result_file),
                        True, 'IOError')

    def help(self):
        return 'No help!'

    @staticmethod
    def get_render(render_name):
        '''
        Returns a derived Render object that correspond
        to 'render_name'. Ex: 'html'
        '''
        LOGGER.info(
            "Requiring render '{0}'".format(render_name))
        render_class = None
        if not CONFIG.has_option('renders', render_name):
            return
        module = CONFIG.get('renders', render_name)
        i = module.rindex('.')
        module_name = module[:i]
        class_name = module[i + 1:]
        try:
            render = import_module(module_name)
            render_class = getattr(render, class_name)
        except Exception as e:
            LOGGER.error(
                "Error loading '{0}' render module. {1}.".format(
                    render_name, e), True)
            return

        if render_class:
            LOGGER.info(
                "Render '{0}' found.".format(render_name))
            return render_class()
        else:
            LOGGER.warn(
                "Render '{0}' not found.".format(render_name))
