import argparse

from jitte.core.testsuite import TestSuite
from jitte.core.renderer import Renderer
from jitte.core.summary import Summary
from jitte.core.logger import logger


def parse_options():
    """
    Process command line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("testpath",
                        type=str,
                        help="Test configuration file path")
    parser.add_argument("resultpath",
                        type=str,
                        help="Result file path")
    parser.add_argument("-t",
                        "--result-title",
                        action="store",
                        type=str,
                        default="Summary",
                        dest="result_title",
                        help="Result file title")

    return parser.parse_args()


if __name__ == '__main__':
    options = parse_options()
    test_suite = TestSuite(logger, options.testpath)
    results = test_suite.run()

    summary_gen = Summary(logger, results)
    summary = summary_gen.create_summary(options.result_title)

    r = Renderer(logger, summary).render(options.resultpath)
