# -*-coding:utf-8-*-
import unittest
from plugs import validator, executor, hooker


class TestPlug(unittest.TestCase):
    '''Test Plug module'''

    def test_validator(self):
        flag, msg = validator.verify("equal", u'测试内容', u'测试内容')
        self.assertEqual(flag, True)
        self.assertEqual(msg, None)

        flag, msg = validator.verify("include", u'abcdefg', u'cde')
        self.assertEqual(flag, True)
        self.assertEqual(msg, None)

        flag, msg = validator.verify("regex", '{"success" : "true"}', 'succ.*')
        self.assertEqual(flag, True)
        self.assertEqual(msg, None)

        flag, msg = validator.verify("json", '{"success" : "true"}', 'true', jsonpath='$.success')
        self.assertEqual(flag, True)
        self.assertEqual(msg, None)

    def test_executor(self):
        pass

    def test_hooker(self):
        pass


if __name__ == '__main__':
    unittest.main()