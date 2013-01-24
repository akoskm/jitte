import shutil
import errno
import os

from datetime import datetime

from jinja2 import Environment, PackageLoader

ASSETS_PATH = "templates/assets"


class Renderer(object):

    def __init__(self, logger, summary):
        self.logger = logger
        self.env = Environment(loader=PackageLoader('jitte', 'templates'))
        self.summary = summary

    def render(self, result_path):
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        template = self.env.get_template('template.html')
        # show result
        s1 = "Tests run: {0}".format(self.summary['total'])
        s2 = "{0} failed. {1} passed.".format(self.summary['fail'],
                                              self.summary['pass'])
        self.printnice(s1, s2, "=")
        # write to file
        filepath = os.path.join(result_path,
                                'result-{0}.html'.format(timestamp))
        self.copy(ASSETS_PATH, result_path)
        with open(filepath, 'w') as output_file:
            output_file.write(template.render(report=self.summary))

    def copy(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

    def printnice(self, s1, s2, headerchar):
        size = 0
        header = ""
        s1_size = len(s1)
        s2_size = len(s2)
        if (s1_size > s2_size):
            size = s1_size
        else:
            size = s2_size

        for i in range(0, size):
            header = header + str(headerchar)

        print header
        print s1
        print s2
        print header
