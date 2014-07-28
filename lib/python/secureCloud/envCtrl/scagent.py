'''
Created on 2012/4/12
@author: eason_lin
'''
import logging
import staf


def scconfig_windows(EndPoint, REMOTE_SCCONFIG_DIR, lstArgs):
    intExitCode, strStdout = staf.call_remote(
        EndPoint, "taskkill", ["/F", "/IM", "scconfig.exe"])
    intExitCode, strStdout = staf.call_remote(EndPoint, '"' + REMOTE_SCCONFIG_DIR + "scconfig.exe" + '"', lstArgs, {'LD_LIBRARY_PATH': ""}, REMOTE_SCCONFIG_DIR)
    #scconfig after fresh install will return 0, after re-install will return 42949697295L
    if intExitCode == "0" or "4294967295L":
        return 0
    else:
        return 1


def install_agent_windows(EndPoint, remote_filepath_exe):
    intExitCode, strStdout = staf.call_remote(
        EndPoint, remote_filepath_exe, [])
    """
    #execute installer fail
    if intExitCode != "0":
        return intExitCode
    """
    #shutdown staf wait reboot
    staf.shutdown(EndPoint)
    logging.info("start to wait staf ...")
    LONGTIMES = 20
    staf.wait_ready(EndPoint, LONGTIMES)
    return intExitCode


def scconfig_linux(EndPoint, REMOTE_SCCONFIG_DIR, lstArgs):
    intExitCode, strStdout = staf.call_remote(
        EndPoint, "killall", ["scconfig.sh"])
    intExitCode, strStdout = staf.call_remote(
        EndPoint, "killall", ["sc_config"])
    intExitCode, strStdout = staf.call_remote(EndPoint, REMOTE_SCCONFIG_DIR +
                                              "scconfig.sh", lstArgs, {'LD_LIBRARY_PATH': ""})
    return intExitCode
