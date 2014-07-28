def isSrverPassbyLogString(str):
    match_str = "Doing action: FatalError"
    match_readme = "Doing action: LaunchReadme"
    index = str.find(match_str)
    if index == -1:
        index = str.find(match_readme)
        if index == -1:
            return False
        else:
            return True
    else:
        return False


def isSrverPassbyLog(path, code):
    """code='utf_16_le'"""
    f = open(path, 'r')
    str = f.read()
    str = str.decode(code)
    return isSrverPassbyLogString(str)


def testIsSrverPassbyLogStringNoLaunchReadmeFile():
    """ Test No LaunchReadmeFile

    >>> testIsSrverPassbyLogStringNoLaunchReadmeFile()
    False
    """
    str = """MSI (s) (C4:90) [18:09:03:008]: Machine policy value 'DisableRollback' is 0
MSI (s) (C4:90) [18:09:03:008]: Incrementing counter to disable shutdown. Counter after increment: 0
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (s) (C4:90) [18:09:03:008]: Restoring environment variables
MSI (s) (C4:90) [18:09:03:023]: Destroying RemoteAPI object.
MSI (s) (C4:10) [18:09:03:023]: Custom Action Manager thread ending.
MSI (c) (9C:DC) [18:09:03:023]: Back from server. Return value: 1603
MSI (c) (9C:DC) [18:09:03:023]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (c) (9C:DC) [18:09:03:023]: PROPERTY CHANGE: Deleting SECONDSEQUENCE property. Its current value is '1'.
Action ended 18:09:03: ExecuteAction. Return value 3.
Action 18:09:03: FatalError.
Action start 18:09:03: FatalError.
Action 18:09:03: FatalError. Dialog created
Action ended 18:09:04: FatalError. Return value 2.
Action ended 18:09:04: INSTALL. Return value 3.
MSI (c) (9C:DC) [18:09:04:305]: Destroying RemoteAPI object."""
    return isSrverPassbyLogString(str)


def testIsSrverPassbyLogStringFatelError():
    """ Test FatelError

    >>> testIsSrverPassbyLogStringFatelError()
    False
    """
    str = """MSI (s) (C4:90) [18:09:03:008]: Machine policy value 'DisableRollback' is 0
MSI (s) (C4:90) [18:09:03:008]: Incrementing counter to disable shutdown. Counter after increment: 0
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (s) (C4:90) [18:09:03:008]: Restoring environment variables
MSI (s) (C4:90) [18:09:03:023]: Destroying RemoteAPI object.
MSI (s) (C4:10) [18:09:03:023]: Custom Action Manager thread ending.
MSI (c) (9C:DC) [18:09:03:023]: Back from server. Return value: 1603
MSI (c) (9C:DC) [18:09:03:023]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (c) (9C:DC) [18:09:03:023]: PROPERTY CHANGE: Deleting SECONDSEQUENCE property. Its current value is '1'.
Action ended 18:09:03: ExecuteAction. Return value 3.
MSI (c) (9C:DC) [18:09:03:023]: Doing action: FatalError
Action 18:09:03: FatalError.
Action start 18:09:03: FatalError.
Action 18:09:03: FatalError. Dialog created
Action ended 18:09:04: FatalError. Return value 2.
Action ended 18:09:04: INSTALL. Return value 3.
MSI (c) (9C:DC) [18:09:04:305]: Destroying RemoteAPI object.
MSI (c) (9C:B8) [18:09:04:305]: Doing action: LaunchReadme."""
    return isSrverPassbyLogString(str)


def testIsSrverPassbyLogString():
    """Test Pass

    >>> testIsSrverPassbyLogString()
    True
    """
    str = u"""MSI (s) (C4:90) [18:09:03:008]: Machine policy value 'DisableRollback' is 0
MSI (s) (C4:90) [18:09:03:008]: Incrementing counter to disable shutdown. Counter after increment: 0
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Note: 1: 1402 2: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Installer\Rollback\Scripts 3: 2
MSI (s) (C4:90) [18:09:03:008]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (s) (C4:90) [18:09:03:008]: Restoring environment variables
MSI (s) (C4:90) [18:09:03:023]: Destroying RemoteAPI object.
MSI (s) (C4:10) [18:09:03:023]: Custom Action Manager thread ending.
MSI (c) (9C:DC) [18:09:03:023]: Back from server. Return value: 1603
MSI (c) (9C:DC) [18:09:03:023]: Decrementing counter to disable shutdown. If counter >= 0, shutdown will be denied.  Counter after decrement: -1
MSI (c) (9C:DC) [18:09:03:023]: PROPERTY CHANGE: Deleting SECONDSEQUENCE property. Its current value is '1'.
Action ended 18:09:03: ExecuteAction. Return value 3.
Action 18:09:03: FatalError.
Action start 18:09:03: FatalError.
Action 18:09:03: FatalError. Dialog created
Action ended 18:09:04: FatalError. Return value 2.
Action ended 18:09:04: INSTALL. Return value 3.
MSI (c) (9C:DC) [18:09:04:305]: Destroying RemoteAPI object.
MSI (c) (9C:B8) [18:09:04:305]: Doing action: LaunchReadme."""
    return isSrverPassbyLogString(str)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
