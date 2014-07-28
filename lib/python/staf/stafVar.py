from tmStafHandle import TmStafHandle


def getVar(strVarName, handle=None, strHost='local'):
    if not handle:
        handle = TmStafHandle(r'Trend\GetVar')
    objResult = handle.submit(strHost, 'var', 'get system var %s' %
                              strVarName, mode=handle.Synchronous)
    if not objResult.isOk():
        raise RuntimeError('get var "%s" failed! Error: %s' % (
            strVarName, objResult))
    else:
        return objResult.getResult()
