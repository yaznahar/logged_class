# -*- coding: utf-8 -*-

import logging
import tempfile
import unittest

import logged_class as lc


CUSTOM_NAME = 'Wittgenstein'


class Empty:
    pass


@lc.logged
class Logged1:
    pass


@lc.logged(name=CUSTOM_NAME)
class Logged2:
    pass


@lc.logger_attr
class Logged3:
    pass


class Logged4(lc.LoggedMixin):
    pass


class Logged5(Logged1):
    pass


class Logged6(Logged2):
    pass


class TestLoggedDecorator(unittest.TestCase):
    def test_attrs(self):
        obj = Logged1()
        self.assertTrue(hasattr(obj, lc.HIDDEN_LOGGER_ATTR))
        self.assertFalse(hasattr(obj, lc.SHORT_LOGGER_ATTR))
        logger = getattr(obj, lc.HIDDEN_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, obj.__class__.__name__)
        for method_name in lc.METHOD_NAMES:
            self.assertTrue(hasattr(obj, method_name))

    def test_custom_name(self):
        obj = Logged2()
        self.assertFalse(hasattr(obj, lc.SHORT_LOGGER_ATTR))
        logger = getattr(obj, lc.HIDDEN_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, CUSTOM_NAME)
        self.assertNotEqual(logger.name, obj.__class__.__name__)

    def test_without_methods(self):
        obj = Logged3()
        self.assertTrue(hasattr(obj, lc.SHORT_LOGGER_ATTR))
        self.assertFalse(hasattr(obj, lc.HIDDEN_LOGGER_ATTR))
        logger = getattr(obj, lc.SHORT_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, obj.__class__.__name__)
        for method_name in lc.METHOD_NAMES:
            self.assertFalse(hasattr(obj, method_name))

    def test_attrs_inheritance(self):
        obj = Logged5()
        self.assertTrue(hasattr(obj, lc.HIDDEN_LOGGER_ATTR))
        self.assertFalse(hasattr(obj, lc.SHORT_LOGGER_ATTR))
        logger = getattr(obj, lc.HIDDEN_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, obj.__class__.__name__)
        obj = Logged6()
        logger = getattr(obj, lc.HIDDEN_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, CUSTOM_NAME)
        logger = getattr(obj, lc.HIDDEN_LOGGER_ATTR)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, CUSTOM_NAME)

    def test_add_log_methods(self):
        obj = Empty()
        logger = logging.getLogger()
        for method_name in lc.METHOD_NAMES:
            self.assertFalse(hasattr(obj, method_name))
        lc.add_log_methods(obj, logger)
        for method_name in lc.METHOD_NAMES:
            method = getattr(obj, method_name)
            self.assertEqual(method.__name__, method_name)
            self.assertEqual(getattr(logger, method_name), method)

    def test_logging_in_file(self):
        obj = Logged2()
        with tempfile.NamedTemporaryFile('r') as fhandler:
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                filename=fhandler.name, filemode='w', level=logging.DEBUG)
            obj.info('Hello')
            content = fhandler.read()
            self.assertIn('Hello', content)
            self.assertIn('INFO', content)
            self.assertIn(CUSTOM_NAME, content)


class TestLoggedMixin(unittest.TestCase):
    def test_attrs(self):
        cls = Logged4
        self.assertIsNone(getattr(cls, lc.HIDDEN_LOGGER_ATTR))
        self.assertFalse(hasattr(cls, lc.SHORT_LOGGER_ATTR))
        for method_name in lc.METHOD_NAMES:
            self.assertTrue(hasattr(cls, method_name))


if __name__ == '__main__':
    unittest.main()
