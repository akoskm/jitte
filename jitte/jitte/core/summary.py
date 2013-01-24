# Desired Format
# [
#   {
#     "name" : "test name",
#     "result" : "ok  / false",
#     "cause" : "if ok empty else text"
#   }
# ]


class Summary(object):

    def __init__(self, logger, results):
        self.logger = logger
        self.results = results

    def create_summary(self, title):
        test_total = len(self.results)
        ok = 0
        fail = 0
        for test in self.results:
            if test['result'] == 'OK':
                ok = ok + 1
            elif test['result'] == 'FAILED':
                fail = fail + 1
            else:
                msg = "Unknown test result: {0}".format(test['result'])
                self.logger.error(msg)

        pass_pct = float(ok) / test_total
        fail_pct = float(fail) / test_total
        summary = {
            "title": title,
            "date": 'timestamphere',
            "total": test_total,
            "pass": ok,
            "pass_pct": '{:.2%}'.format(pass_pct),
            "fail": fail,
            "fail_pct": '{:.2%}'.format(fail_pct),
            "tests": self.results
        }
        return summary
