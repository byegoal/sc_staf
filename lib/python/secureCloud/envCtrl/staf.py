'''
Created on 2011/8/1
@author: eason
'''
import time
import os
import logging
import tmstaf.callPyFunction
from tmstaf.stafServices import ProductStafProcessService, StafProcessServiceAsync, freeProcess, shutdown
from subprocess import PIPE, Popen, STDOUT


def wait_ready(strEndpoint, intTimes=3):
    logging.info("wait STAF service until ready")
    for i in range(intTimes):
        time.sleep(1.0)
        p = Popen("staf " + strEndpoint + " ping ping", shell=True,
                  stdin=PIPE, stdout=PIPE)
        try:
            if p.wait() == 0:
                return 0

        except RuntimeError:
            import sys
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))
            continue

        logging.debug(p.stdout.readlines())
        logging.info("waiting staf service [%s] count [%i]" % (strEndpoint, i))
    return 1


def wait_stop(strEndpoint, intTimes=1):
    # wait until STAF service is stop
    logging.info("# wait until STAF service is stop")
    for i in range(intTimes):
        p = Popen("staf " + strEndpoint + " ping ping", shell=True,
                  stdin=PIPE, stdout=PIPE)
        if p.wait() != 0:
            return 1
        time.sleep(1.0)
    return 0


def wait_reboot(strEndpoint, intTimes=1):
    if wait_stop(strEndpoint, intTimes) == 0:
        return 0
    if wait_ready(strEndpoint, intTimes) == 0:
        return 0
    return 1


def call_remote(strDestIp, strExecutable, lstArgs, dicEnv={}, workdir=None, intTimeout=600):
    logging.debug("Execute [" + strExecutable + " " + " ".join(lstArgs) + "]")
    logging.debug("Environment [" + str(dicEnv) + "]" + " Work Dir [" +
                  str(workdir) + "]")
    intLogLevel = os.getenv("TMSTAF_LOG_LEVEL")
    dicEnv['TMSTAF_LOG_LEVEL'] = str(intLogLevel)
    objStafProcessService = ProductStafProcessService(
        intTimeout, dicEnv, workdir)
    return objStafProcessService.call(strDestIp, strExecutable, lstArgs)


def call_local(strExecutable, lstArgs, dicEnv={}, workdir=None, intTimeout=600):
    lstArgs.insert(0, strExecutable)
    intLogLevel = os.getenv("TMSTAF_LOG_LEVEL")
    dicEnv['TMSTAF_LOG_LEVEL'] = str(intLogLevel)
    dicOSEnv = os.environ.copy()
    dicEnv = dicOSEnv.update(dicEnv)
    p = Popen(lstArgs, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              env=dicEnv, universal_newlines=True, shell=True)
    strStdout = p.stdout.read()
    for i in range(intTimeout):
        intExitCode = p.poll()
        if intExitCode is not None:
            break
        time.sleep(1)
    if intExitCode is None:
        raise RuntimeError('Wait process finished timeout!')
    return intExitCode, strStdout


def call_remote_async(strDestIp, strExecutable, lstArgs, dicEnv={}, workdir=None, intTimeout=600, trace=True):
    logging.debug("Execute [" + strExecutable + " " + " ".join(lstArgs) + "]")
    intLogLevel = os.getenv("TMSTAF_LOG_LEVEL")
    dicEnv['TMSTAF_LOG_LEVEL'] = str(intLogLevel)
    logging.debug("Environment [" + str(dicEnv) + "]" + " Work Dir [" +
                  str(workdir) + "]")
    objStafProcessService = StafProcessServiceAsync(dicEnv, workdir)
    processHandle, handleClass = objStafProcessService.call(
        strDestIp, strExecutable, lstArgs)
    #intExitCode = waitProcess(strDestIp,processHandle,intTimeout)
    intExitCode, stdout, stderr = handleClass.waitProcess(intTimeout, trace)
    if trace:
        logging.debug("""
        ======== stdout ========
        %s
        ======== stderr ========
        %s
        ==================""" % (stdout, stderr))
    freeProcess(strDestIp, processHandle)
    return intExitCode


def call_remote_python_async(strDestIp, strModuleName, strFuncName, lstArgs, dicEnv={}, workdir=None, intTimeout=600, trace=True):
    logging.debug("Execute [\nfrom " + strModuleName + " import " + strFuncName + "\n" + strFuncName + "(" + ",".join(lstArgs) + ")\n]")
    intLogLevel = os.getenv("TMSTAF_LOG_LEVEL")
    dicEnv['TMSTAF_LOG_LEVEL'] = str(logging.DEBUG)
    logging.debug("Environment [" + str(dicEnv) + "]" + " Work Dir [" +
                  str(workdir) + "]")
    objStafProcessService = StafProcessServiceAsync(dicEnv, workdir)
    lstArgs = processArgs(strModuleName, strFuncName, lstArgs)
    processHandle, handleClass = objStafProcessService.call(
        strDestIp, "callPyFunction", lstArgs)
    #intExitCode = waitProcess(strDestIp,processHandle,intTimeout)
    intExitCode, stdout, stderr = handleClass.waitProcess(intTimeout, trace)
    if trace:
        logging.debug("""
        ======== stdout ========
        %s
        ======== stderr ========
        %s
        ==================""" % (stdout, stderr))
    freeProcess(strDestIp, processHandle)
    return intExitCode


def call_remote_python(strDestIp, strModuleName, strFuncName, lstArgs, dicEnv={}, workdir=None, intTimeout=600):
    logging.debug("Execute [\nfrom " + strModuleName + " import " + strFuncName + "\n" + strFuncName + "(" + ",".join(lstArgs) + ")\n]")
    logging.debug("Environment [" + str(dicEnv) + "]" + " Work Dir [" +
                  str(workdir) + "]")
    intLogLevel = os.getenv("TMSTAF_LOG_LEVEL")
    dicEnv['TMSTAF_LOG_LEVEL'] = str(intLogLevel)
    objStafProcessService = ProductStafProcessService(
        intTimeout, dicEnv, workdir)
    lstArgs = processArgs(strModuleName, strFuncName, lstArgs)
    return objStafProcessService.call(strDestIp, "callPyFunction", lstArgs)


def processArgs(strModuleName, strFuncName, lstArgs):
    lstOutput = [strModuleName, strFuncName]
    strArgs = tmstaf.callPyFunction.encodeCmdLine(lstArgs)
    lstOutput.append(strArgs)
    return lstOutput

if __name__ == '__main__':
    strDestIp = "ec2-175-41-159-193.ap-southeast-1.compute.amazonaws.com"
    intExitCode, strStdout = call_remote(
        strDestIp, "env", [], {'LD_LIBRARY_PATH': ""})
    print strStdout
    strDestIp = "ec2-175-41-159-193.ap-southeast-1.compute.amazonaws.com"
    intExitCode, strStdout = call_remote_python(
        strDestIp, "os", "getenv", ["PATH"], {'LD_LIBRARY_PATH': ""})
    print strStdout
