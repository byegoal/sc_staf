import sys
import logging
import os
import binascii


def initConsoleLog(intDebugLevel):
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s.%(msecs)d %(levelname)-6s %(message)s', datefmt='%H:%M:%S', level=intDebugLevel)


def encodeCmdLine(lstArgs):
    strArgs = binascii.b2a_base64(str(lstArgs))[:-1]
    return strArgs


def decodeCmdLine(strArgs):
    lstArgs = eval(binascii.a2b_base64(strArgs))
    return lstArgs


def addTmstafLibPath():
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(__file__) or os.getcwd()))


def main():
    addTmstafLibPath()
    intLogLevel = int(os.environ.get('TMSTAF_LOG_LEVEL', logging.DEBUG))
    initConsoleLog(intLogLevel)
    strModule, strFunc = sys.argv[1:3]
    strArgs = sys.argv[3]
    lstArgs = decodeCmdLine(strArgs)
    logging.info('call %s.%s%s', strModule, strFunc, tuple(lstArgs))
    exec 'from %s import %s' % (strModule, strFunc)
    func = eval(strFunc)
    result = func(*lstArgs)
    logging.info('return %s', result)
    return result

if __name__ == '__main__':
    sys.exit(main())
