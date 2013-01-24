import unittest

from jitte.core.testcase import TestCase
from jitte.core.exceptions import TestError, ReplyNotAvailable
from jitte.tests.mocks import MockedLogger, MockedReply


class TestCaseMethods(unittest.TestCase):

    def setUp(self):
        self.test_case = TestCase(MockedLogger(),
                                  'get',
                                  'http://www.google.com/',
                                  [],
                                  [],
                                  {},
                                  None)

    def test_find_by_xpath_ok(self):
        source = '<xml><tree><branch><leaf>this</leaf></branch></tree></xml>'
        xpath = '//leaf/text()'
        expected = 'this'
        result = self.test_case._find_by_xpath(source, xpath)
        self.assertEqual(result, expected)

    def test_find_by_xpath_not_found(self):
        source = '<xml><tree><branch><leaf>this</leaf></branch></tree></xml>'
        xpath = '//invalid/xpath'
        expected = TestError
        self.assertRaises(expected,
                          self.test_case._find_by_xpath,
                          source,
                          xpath)

    def test_find_by_xpath_multiple_results(self):
        source = ('<xml><tree><branch><leaf>this</leaf>'
                  '<leaf>this</leaf></branch></tree></xml>')
        xpath = '//leaf/text()'
        expected = TestError
        self.assertRaises(expected,
                          self.test_case._find_by_xpath,
                          source,
                          xpath)

    def test_find_by_xpath_in_empty_response(self):
        source = ''
        xpath = '//leaf/text()'
        expected = TestError
        self.assertRaises(expected,
                          self.test_case._find_by_xpath,
                          source,
                          xpath)

    def test_find_in_json_ok(self):
        source = '{"tree": {"branch": {"leaf": {"1": "this"}}}}'
        key_list = ['tree', 'branch', 'leaf', '1']
        expected = 'this'
        result = self.test_case._find_in_json(source, key_list)
        self.assertEqual(result, expected)

    def test_find_in_json_invalid_json(self):
        source = '{"tree": {"branch": {"leaf": {"1": this}}}}'
        key_list = ['tree', 'branch', 'leaf', '1']
        expected = TestError
        self.assertRaises(expected,
                          self.test_case._find_in_json,
                          source,
                          key_list)

    def test_find_in_json_not_found(self):
        source = '{"tree": {"branch": {"leaf": {"1": "this"}}}}'
        key_list = ['tree', 'branch', 'leaf', '2']
        expected = TestError
        self.assertRaises(expected,
                          self.test_case._find_in_json,
                          source,
                          key_list)

    def test_check_json_pass(self):
        reply = MockedReply('{"tree": {"branch": {"leaf": {"1": "this"}}}}',
                            200)
        result = self.test_case._check('json',
                                       'eq',
                                       'this',
                                       ['tree', 'branch', 'leaf', '1'],
                                       reply)
        self.assertEqual(result, True)

    def test_check_json_wont_pass(self):
        reply = MockedReply('{"tree": {"branch": {"leaf": {"1": "this"}}}}',
                            200)
        result = self.test_case._check('json',
                                       'neq',
                                       'this',
                                       ['tree', 'branch', 'leaf', '1'],
                                       reply)
        self.assertEqual(result, False)

    def test_check_xpath_pass(self):
        xml = '<xml><tree><branch><leaf>this</leaf></branch></tree></xml>'
        reply = MockedReply(xml, 200)
        result = self.test_case._check('xpath',
                                       'eq',
                                       'this',
                                       '/xml/tree/branch/leaf/text()',
                                       reply)
        self.assertEqual(result, True)

    def test_check_xpath_wont_pass(self):
        xml = '<xml><tree><branch><leaf>this</leaf></branch></tree></xml>'
        reply = MockedReply(xml, 200)
        result = self.test_case._check('xpath',
                                       'eq',
                                       'this',
                                       '/xml/tree/branch/invalid/@value',
                                       reply)
        self.assertEqual(result, False)

    def test_check_status_code_pass(self):
        reply = MockedReply(None, 200)
        result = self.test_case._check('status_code',
                                       'eq',
                                       '200',
                                       None,
                                       reply)
        self.assertEqual(result, True)

    def test_check_status_code_wont_pass(self):
        reply = MockedReply(None, 400)
        result = self.test_case._check('status_code',
                                       'neq',
                                       '400',
                                       None,
                                       reply)
        self.assertEqual(result, False)

    def test_check_static_pass(self):
        html = '<html><head></head><body>foo</body></html>'
        reply = MockedReply(html, 200)
        result = self.test_case._check('static',
                                       'eq',
                                       html,
                                       None,
                                       reply)
        self.assertEqual(result, True)

    def test_check_static_wont_pass(self):
        html = '<html><head></head><body>bar</body></html>'
        reply = MockedReply(html, 200)
        result = self.test_case._check('static',
                                       'neq',
                                       html,
                                       None,
                                       reply)
        self.assertEqual(result, False)
