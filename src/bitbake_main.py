'''
Created on Dec 12, 2016

@author: xiaopan
'''
import getopt
import sys

from check.post_check import BitbakePostCheck
from utils.log import Log


if __name__ == '__main__':
    OPTS, ARGS = getopt.getopt(sys.argv[1:], 'b:', 'baseline')
    logger = Log().getLogger("Main")
    baseline = ""
    for opt, arg in OPTS:
        if opt in ['-b', '--baseline']:
            baseline = arg
    if baseline == "":
        logger.error("please run the script with parameter -b <baseline> ")
    BitbakePostCheck(baseline).start()
