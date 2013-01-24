import sys
import logging


logging.getLogger('').setLevel(logging.DEBUG)
logger = logging.getLogger('jitte')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(handler)
