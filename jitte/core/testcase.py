import json
import time

import requests
from lxml import etree

from jitte.core.exceptions import TestError, ReplyNotAvailable


class TestCase(object):

    def __init__(self, logger, method, url, assume, data, headers, p_reply):
        self.logger = logger
        self.method = method
        self.url = url
        self.assume = assume
        self.data = data
        self.headers = headers
        self.p_reply = p_reply

    def invoke(self):
        start = time.time()
        result = {'cause': '',
                  'result': 'FAILED',
                  'reply': None}
        try:
            reply = self._make_request()
        except TestError as te:
            result['cause'] = str(te)
        else:
            result['reply'] = reply
            if reply.status_code >= 400:
                cause = 'Got status_code: {0}'.format(reply.status_code)
                result['cause'] = cause
            else:
                process_result = self._process_reply(reply)
                if process_result:
                    result.update(process_result)
                else:
                    result['result'] = 'OK'

        result['duration'] = '{0:.5f}'.format(time.time() - start)
        return result

    def _make_request(self):
        self.logger.info('Requesting => {0}'.format(self.url))
        try:
            send_data = self._process_data(self.data)
        except ReplyNotAvailable:
            msg = 'Request failed, previous reply not available.'
            raise TestError(msg)

        try:
            key = 'params' if isinstance(send_data, dict) else 'data'
            kwargs = {key: send_data}
            reply = requests.request(self.method,
                                     self.url,
                                     headers=self.headers,
                                     **kwargs)
        except requests.exceptions.RequestException as exc:
            msg = 'Request failed: {0}'.format(exc)
            raise TestError(msg)

        return reply

    def _process_data(self, raw_data):
        params = dict()
        for param in raw_data:
            if 'param_name' not in param:
                # this is most likely a file type, so just return the
                # value as it will be posted as string, not as dict
                return param['param_value']['value']

            param_name = param['param_name']
            param_value = param['param_value']

            name = self._parse_value(param_name['type'],
                                     param_name['value'])
            value = self._parse_value(param_value['type'],
                                      param_value['value'])
            params[name] = value

        return params

    def _find_in_json(self, source, value):
        try:
            prev_json = json.loads(source)
        except Exception as exc:
            raise TestError('JSON Parse error: {0}'.format(exc))
        try:
            for item in value:
                prev_json = prev_json[item]
        except KeyError:
            raise TestError('JSON Key {0} not found'.format(item))

        return prev_json

    def _find_by_xpath(self, source, xpath):
        try:
            prev_xml = etree.fromstring(source)
        except Exception as exc:
            raise TestError('XML Parse error: {0}'.format(exc))

        try:
            (result,) = prev_xml.xpath(xpath)
            return result
        except Exception as exc:
            msg = 'XPath {0} evaluation error: {1}'.format(xpath, exc)
            raise TestError(msg)

    def _parse_value(self, p_type, value):
        if p_type in ('json', 'xpath') and self.p_reply is None:
            raise ReplyNotAvailable()

        if p_type == 'json':
            return self._find_in_json(self.p_reply.text, value)
        elif p_type == 'xpath':
            return self._find_by_xpath(self.p_reply.text, value)
        else:
            return value

    def _process_reply(self, reply):
        for assumption in self.assume:
            assumption_type = assumption['type']
            cond = assumption['pass_if']
            expected = assumption['expected']
            assumption_got = assumption['got']

            if not self._check(assumption_type,
                               cond,
                               expected,
                               assumption_got,
                               reply):
                return {'assumption': assumption,
                        'condition': cond,
                        'got': reply.text}

    def _check(self, assumption_type, cond, expected, assumption_got, got):
        try:
            if assumption_type == 'json':
                got = self._find_in_json(got.text, assumption_got)
            elif assumption_type == 'xpath':
                got = self._find_by_xpath(got.text, assumption_got)
            elif assumption_type == 'status_code':
                got = str(got.status_code)
            else:
                got = got.text
        except TestError:
            return False
        else:
            return self._validate(got, expected, cond)

    def _validate(self, got, expected, condition):
        checks = {'eq': lambda x, y: x == y,
                  'neq': lambda x, y: x != y,
                  'in': lambda x, y: y in x,
                  'nin': lambda x, y: y not in x,
                  'empty': lambda x, y: x is None,
                  'nempty': lambda x, y: x is not None,
                  'ninja': lambda x, y: True}
        return checks[condition](got, expected)
