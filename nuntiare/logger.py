# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.
import logging
import logging.handlers


class NuntiareLog:
    def __init__(self, default_level="WARNING"):
        default_level = self._get_level_from_string(default_level)
        self._logger = logging.getLogger('Nuntiare')
        self._logger.setLevel(default_level)
        self.add_handler(logging.NullHandler())

    def add_handler(self, handler, level=None, formatter=None):
        if level:
            handler.setLevel(self._get_level_from_string(level))
        if formatter:
            handler.setFormatter(logging.Formatter(formatter))
        self._logger.addHandler(handler)

    def remove_handler(self, handler):
        self._logger.removeHandler(handler)

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warn(self, message):
        self._logger.warning(message)

    def error(self, message, raise_error=False, error_type=None):
        self._raise_error_with_log(
            message, logging.ERROR, raise_error, error_type)

    def critical(self, message, raise_error=False, error_type=None):
        self._raise_error_with_log(
                message, logging.CRITICAL,
                raise_error, error_type)

    def _raise_error_with_log(self, message, log_type,
                              raise_error, error_type):
        if log_type == logging.ERROR:
            self._logger.error(message)
        else:
            self._logger.critical(message)
        if raise_error:
            if not error_type or error_type == 'ValueError':
                raise ValueError(message)
            elif error_type == 'IOError':
                raise IOError(message)
            # TODO other types
            raise Exception(message)

    def _get_level_from_string(self, level):
        if level == "DEBUG":
            return logging.DEBUG
        elif level == "INFO":
            return logging.INFO
        elif level == "WARNING":
            return logging.WARNING
        elif level == "ERROR":
            return logging.ERROR
        elif level == "CRITICAL":
            return logging.CRITICAL
        err_msg = "Invalid logging type '{0}'. " \
            "It must be: DEBUG, INFO, WARNING, ERROR or CRITICAL"
        raise ValueError(err_msg.format(level))
