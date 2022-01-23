#!/usr/bin/env python3
"""Module to add logger to objects"""


import logging
from functools import partial, partialmethod, wraps


METHOD_NAMES = ('debug', 'info', 'warning', 'error', 'critical', 'exception')
HIDDEN_LOGGER_ATTR = '_logger'
SHORT_LOGGER_ATTR = 'log'


def add_log_methods(obj, logger):
    """Add logger methods (debug, info, etc) to the class"""
    for method_name in METHOD_NAMES:
        method = getattr(logger, method_name)
        setattr(obj, method_name, method)


def logged(cls=None, *, name='', attr_name=HIDDEN_LOGGER_ATTR, add_methods=True):
    """Decorator to add logger attribute and methods to objects"""
    def logged_for_init(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger_name = name or self.__class__.__name__
            logger = logging.getLogger(logger_name)
            setattr(self, attr_name, logger)
            if add_methods:
                add_log_methods(self, logger)
            return func(self, *args, **kwargs)
        return wrapper

    def wrap(cls):
        cls.__init__ = logged_for_init(cls.__init__)
        return cls

    return wrap if cls is None else wrap(cls)


logger_attr = partial(logged, add_methods=False, attr_name=SHORT_LOGGER_ATTR)


class LoggedMixin:
    """Implement optional logging methods"""
    _logger = None

    @classmethod
    def set_default_logger(cls, logger):
        cls._logger = logger

    def set_logger(self, logger):
        self._logger = logger

    def _log_method(self, msg, *args, **kwargs):
        """Proxy method to call real log function according to severity"""
        if self._logger is None:
            return
        log_level_name = kwargs.pop('_severity', 'debug')
        real_log_method = getattr(self._logger, log_level_name, None)
        if real_log_method is not None:
            real_log_method(msg, *args, **kwargs)

    debug = partialmethod(_log_method, _severity='debug')
    info = partialmethod(_log_method, _severity='info')
    warning = partialmethod(_log_method, _severity='warning')
    error = partialmethod(_log_method, _severity='error')
    critical = partialmethod(_log_method, _severity='critical')
    exception = partialmethod(_log_method, _severity='exception')
