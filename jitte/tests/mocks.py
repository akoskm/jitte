

class MockedLogger(object):

    def info(self, message):
        pass

    def debug(self, message):
        pass

    def error(self, message):
        pass


class MockedReply(object):

    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code
