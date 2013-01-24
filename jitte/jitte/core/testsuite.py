import json

from jitte.core.testcase import TestCase
from jitte.core.exceptions import InvalidConfiguration


VALID_ASSUMPTION_TYPES = ('text', 'file', 'status_code', 'json', 'xpath')
VALID_CONDITIONS = ('eq', 'neq', 'in', 'nin', 'ninja', 'empty', 'nempty')
VALID_PARAM_TYPES = ('static', 'file', 'xpath', 'json')


class TestSuite(object):

    def __init__(self, logger, testfile):
        self.logger = logger
        try:
            with open(testfile, 'r') as file_obj:
                s = file_obj.read()
                self.tests = json.loads(s)
        except ValueError:
            msg = 'Invalid test configuration file {0}'.format(testfile)
            self.logger.error(msg)
            exit()
        except IOError:
            msg = 'Test configuration file {0} not found'.format(testfile)
            self.logger.error(msg)
            exit()

    def _clean_method(self, step_id, method):
        cleaned_method = method.lower()
        if cleaned_method not in ("get", "head", "post", "put", "delete"):
            msg = 'Method "{0}" not allowed in step: {1}.'.format(method,
                                                                  step_id)
            raise InvalidConfiguration(msg)

        return cleaned_method

    def _clean_url(self, step_id, url):
        if url is None:
            msg = 'URL not specified in step: {0}.'.format(step_id)
            raise InvalidConfiguration(msg)

        return url

    def _read_file(self, filepath):
        try:
            with open(filepath, 'r') as file_obj:
                return file_obj.read()
        except IOError:
            msg = 'Unable to open: {0}'.format(filepath)
            raise InvalidConfiguration(msg)

    def _clean_assumptions(self, step_id, assumptions):
        if not assumptions:
            msg = 'No assumptions found in step: {0}.'.format(step_id)
            raise InvalidConfiguration(msg)

        cleaned_assumptions = []
        for assumption in assumptions:
            assumption_type = assumption.get('type', 'text').lower()
            if assumption_type not in VALID_ASSUMPTION_TYPES:
                msg = ('Assumption type {0} invalid in '
                       'step: {1}.'.format(assumption_type, step_id))
                raise InvalidConfiguration(msg)

            pass_if = assumption.get('pass_if', 'eq').lower()
            if pass_if not in VALID_CONDITIONS:
                msg = ('Assumption condition {0} invalid in '
                       'step {1}'.format(pass_if, step_id))
                raise InvalidConfiguration(msg)

            expected = assumption.get('expected', None)
            if (not isinstance(expected, basestring) and
                    pass_if not in ('empty', 'nempty')):
                msg = ('Assumption expectation invalid or not specified in '
                       'step {0}'.format(step_id))
                raise InvalidConfiguration(msg)

            assumption_got = assumption.get('got', None)
            try:
                if assumption_type == 'xpath':
                    assert isinstance(assumption_got, basestring)
                elif assumption_type == 'json':
                    # json param must be a list of strings
                    assert isinstance(assumption_got, list)
                    for k in assumption_got:
                        assert isinstance(k, (int, basestring))
            except AssertionError:
                msg = 'Assumption got invalid in step {0}'.format(step_id)
                raise InvalidConfiguration(msg)

            if assumption_type == 'file':
                expected = self.__read_file(expected)

            valid_assumption = {'type': assumption_type,
                                'pass_if': pass_if,
                                'expected': expected,
                                'got': assumption_got}
            cleaned_assumptions.append(valid_assumption)

        return cleaned_assumptions

    def _clean_data(self, step_id, data):

        def get_param(package, param_key):
            # return param_name or param_value from the param package
            try:
                return pkg[param_key]
            except KeyError:
                msg = ('send_data {0} not found in step {1}'.format(param_key,
                                                                    step_id))
                raise InvalidConfiguration(msg)

        def check_type(param_type):
            try:
                assert param_type in VALID_PARAM_TYPES
            except AssertionError:
                msg = ('Invalid send_data param type {0} in '
                       'step {1}'.format(param_type, step_id))
                raise InvalidConfiguration(msg)

        def check_value(param, param_type):
            try:
                if param_type == 'file':
                    # for file types we don't return the filepath as it is, but
                    # read the file ahead and return the data it contains
                    assert isinstance(param['value'], basestring)
                    return self._read_file(param['value'])
                if param_type in ('static', 'xpath'):
                    assert isinstance(param['value'], basestring)
                elif param_type == 'json':
                    # json param must be a list of strings
                    assert isinstance(param['value'], list)
                    for k in param['value']:
                        assert isinstance(k, (int, basestring))
                # all other types are just returned if they pass the validation
                return param['value']
            except (AssertionError, KeyError):
                msg = ('Invalid send_data param in step {0}'.format(step_id))
                raise InvalidConfiguration(msg)

        if not isinstance(data, list):
            msg = 'Invalid send_data in step {0}'.format(step_id)
            raise InvalidConfiguration(msg)

        cleaned_data = []
        for pkg in data:
            param_value = get_param(pkg, 'param_value')
            param_value_type = param_value.get('type', 'static').lower()
            check_type(param_value_type)
            value = check_value(param_value, param_value_type)
            clean_pkg = {'param_value': {'type': param_value_type,
                                         'value': value}}

            if param_value_type == 'file':
                # in case of files param_name is not needed and only
                # one file can be sent, no additional params
                return [clean_pkg]

            param_name = get_param(pkg, 'param_name')
            param_name_type = param_name.get('type', 'static').lower()
            check_type(param_name_type)
            value = check_value(param_name, param_name_type)

            clean_pkg['param_name'] = {'type': param_name_type,
                                       'value': value}

            cleaned_data.append(clean_pkg)

        return cleaned_data

    def _clean_headers(self, step_id, headers):
        if isinstance(headers, dict):
            for hdr_name, hdr_value in headers.items():
                if not isinstance(hdr_name, basestring):
                    break
                if not isinstance(hdr_value, basestring):
                    break
            else:
                return headers

        msg = 'Invalid request header(s) in step {0}'.format(step_id)
        raise InvalidConfiguration(msg)

    def _clean(self, step_id, method, url, assume, data, headers):
        """
        Test the configuration file validity.
        """
        method = self._clean_method(step_id, method)
        url = self._clean_url(step_id, url)
        assumptions = self._clean_assumptions(step_id, assume)
        data = self._clean_data(step_id, data)
        headers = self._clean_headers(step_id, headers)
        return  {"method": method,
                 "url": url,
                 "assume": assumptions,
                 "data": data,
                 "headers": headers}

    def run(self):
        p_reply = None
        next_step = "1"
        executed_steps = []
        results = []

        while next_step is not None:
            executed_steps.append(next_step)
            try:
                request_data = self.tests[next_step]
            except KeyError:
                self.logger.error('Step {0} not found.'.format(next_step))
                break

            cleaned = self._clean(next_step,
                                  request_data.get('method', ''),
                                  request_data.get('url', None),
                                  request_data.get('assume', list()),
                                  request_data.get('send_data', list()),
                                  request_data.get('headers', dict()))
            cleaned['p_reply'] = p_reply
            t = TestCase(self.logger, **cleaned)
            result = t.invoke()
            result['step'] = next_step
            result['url'] = request_data.get('url', None)
            result['assumptions'] = cleaned['assume']
            p_reply = result.pop('reply')
            results.append(result)

            next_step = request_data.get('next', None)
            if next_step in executed_steps:
                self.logger.warning('WARNING! possible infinite loop.')

        return results
