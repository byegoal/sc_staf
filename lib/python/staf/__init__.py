import os
import sys


def findPyStafPath():
    for strPath in sys.path:
        if os.path.exists(os.path.join(strPath, 'PySTAF.py')):
            return strPath
    return ''

try:
    import PySTAF
except ImportError, e:
    if e.message.find('conflicts with this version of Python') >= 0:
        raise ImportError('Please patch STAF Python library in %s according to your Python version.' % (findPyStafPath()))
    else:
        raise ImportError('Please install STAF first. Download site: http://staf.sourceforge.net/')
