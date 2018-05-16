# -*-coding:utf-8-*-
import sys
import unittest


class TestAPICore(unittest.TestCase):
    '''Test API Core module'''

    def test_parse_args(self):
        from bin.api_core import parse_args
        args = ['-u', 'http://www.baidu.com', '-m', 'get', '-d', '{"name":"test"}', '-H', '{"key":"header1"}',
                '-f', 'a.txt:b.txt', '-e', 'utf-8', '-E', 'result', '-C', 'config file', '-D', 'DB:STR',
                '-N', 'test name', '-P', '2', '-c', 'cate', '-t', 'tag', '-v', '2.0.1', '-q', ]
        sys.argv.extend(args)
        actual = parse_args()
        expect = {'files': [('a.txt', 'b.txt')], 'config_file': 'config file', 'encoding': 'utf-8', 'test_priority': 2, 'tag': 'tag', 'expect': 'result', 'test_name': 'test name', 'data': {u'name': u'test'}, 'category': 'cate', 'db_str': 'DB:STR', 'url': 'http://www.baidu.com', 'headers': {u'key': u'header1'}, 'version': '2.0.1', 'method': 'get'}
        self.assertEqual(actual, expect)


if __name__ == '__main__':
    unittest.main()