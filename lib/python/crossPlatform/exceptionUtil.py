import sys
import traceback
import cStringIO


class TimeoutError(Exception):
    pass


def printException():
    print getException()


def getException():
    f = cStringIO.StringIO()
    f.write('Traceback (most recent call last):\n')
    lstTmp = traceback.extract_stack(sys.exc_info()[2].tb_frame)
    lstTmp = lstTmp[:-1]  # remove getException self
    x = traceback.extract_tb(sys.exc_info(
        )[2])  # retrieve exception stack inside "try" statement
    lstTmp.extend(x)
    for lst in lstTmp:
        f.write('  File "%s", line %s, in %s\n' % lst[:3])
        if lst[3]:
            f.write('    %s\n' % lst[3])
    exc_type, exc_value = sys.exc_info()[:2]
    f.write('%s: %s\n' % (exc_type.__name__, exc_value))
    return f.getvalue()


def test():
    def errorFunc():
        a = 1
        b = 2
        raise NameError('aa')
        c = d + e
    try:
        f = 1
        errorFunc()
    except:
        print getException()


def test1():
    try:
        a = a + 1
    except:
        printException()


def test2():
    try:
        import urllib
        urllib.urlopen('http://camge.lo')
    except:
        printException()

strDataCode = '''
a=1
b=2
c=3
print a+b+c+d
'''


def test3():
    strFileName = 'testByCamge.py'
    open(strFileName, 'wb').write(strDataCode)
    try:
        exec open(strFileName) in globals(), locals()
    except:
        printException()
    import os
    os.remove(strFileName)


def test4():
    strModuleName, strFuncName = 'trend.registryUtil', 'valueExist'
    try:
        exec 'from %s import %s' % (strModuleName, strFuncName)
        func = eval(strFuncName)
        func('abc', '123')
    except:
        printException()


if __name__ == '__main__':
    test()
    test1()
    test2()
    test3()
    test4()
