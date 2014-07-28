"""
The crossplatform need utility
"""
import inspect
import time
import logging
import traceback
from types import *
from PySTAF import *


class StafService:
    """
    Provide STAF service
    """
    def __init__(self):
        """
        Get staf handle
        """
        try:
            self.handle = STAFHandle("deployScript")
            self.resultContent = ''
        except STAFException, e:
            print "Error registering with STAF, RC: %d" % e.rc
            import sys
            sys.exit(e.rc)

    def callStafService(self, host, service, cmd):
        """
        Call STAF command
        @param host: host data
        @param service: staf service
        @param cmd: relative serive cmd
        @return:
            0: OK
            1: NG
        """
        #ex. result = handle.submit("local", "ping", "ping")
        result = self.handle.submit(host, service, cmd)
        time.sleep(1)
        self.resultContent = result.result
        if (result.rc != 0):
            print "Error submitting request, RC: %d, Result: %s" % \
                  (result.rc, result.result)
            return 1
        return 0

    def __del__(self):
        """
        Destroy staf handle
        """
        rc = self.handle.unregister()


def check_type(obj, atts=[], callables=[]):
    """
    Check object's type
    @param atts:
    @param callables:
    @return:
        -1 : OK
        0 : NG
    """
    got_atts = True
    for att in atts:
        if not hasattr(obj, att):
            got_atts = False
            break
    got_callables = True
    for call in callables:
        if not hasattr(obj, call):
            got_callables = False
            break
        the_attr = getattr(obj, call)
        if not callable(the_attr):
            got_callables = False
            break
    if got_atts and got_callables:
        return -1
    return 0


def is_iter(obj):
    """
    Check object is List, Tuple, Dict or File type?
    @param obj: the check object
    """
    if isinstance(obj, ListType):
        return 1
    if isinstance(obj, TupleType):
        return 1
    if isinstance(obj, DictType):
        return 1
    if isinstance(obj, FileType):
        return 1
    try:
        iter(obj)
        return -1
    except TypeError:
        return 0


def is_gen(obj):
    """
    Check object is Generator type?
    @param obj: the check object
    @return:
        1: OK
        0: NG
    """
    if isinstance(obj, GeneratorType):
        return 1
    return 0


def is_seq(obj):
    """
    Check object is list, tuple type?
    @param obj: the check object
    @return:
        -1: OK
        0: NG
    """
    if isinstance(obj, ListType):
        return 1
    if isinstance(obj, TupleType):
        return 1
    if is_iter(obj):
        try:
            obj[0:0]
            return -1
        except TypeError:
            pass
    return 0


def is_mapping(obj):
    """
    Check object is Dict type?
    @param obj: the check object
    @return:
        1: OK
        0: NG
    """
    if isinstance(obj, DictType):
        return 1
    if is_iter(obj):
        return check_type(obj, callables=['iteritems', 'has_key'])
    return 0


def is_list(obj):
    """
    Check object is List type?
    @param obj: the check object
    @return:
        1: OK
        0: NG
    """
    if isinstance(obj, ListType):
        return 1
    if is_seq(obj):
        if check_type(obj, callables=['append', 'extend'  'pop']):
            return -1
        return 0


def is_str(obj):
    """
    Check object is String type?
    @param obj: the check object
    @return:
        1: OK
        0: NG
    """
    if isinstance(obj, basestring):
        return 1
    if is_iter(obj):
        if check_type(obj, callables=['index', 'count', 'replace']):
            return -1
    return 0


def is_file(obj):
    """
    Check object is File type?
    @param obj: the check object
    @return:
        -1: OK
        0: NG
    """
    if isinstance(obj, FileType):
        return 1
    if check_type(obj, callables=['read', 'close']):
        return -1
    return 0


def check_all(obj):
    """
    Check object is All  type?
    @param obj: the check object
    @return:
        type string
    """
    result = [str(i) for i in (is_iter(obj), is_gen(obj), is_seq(obj),
                               is_list(obj), is_str(obj), is_mapping(obj),
                               is_file(obj))]
    return '\t'.join(result)


class GetIniSetting:
    """
    ini opoeration module
    """
    def __init__(self, filename=None):
        from trend.config_obj import ConfigObj
        self._cfgpath = filename
        self._cfgfile = ConfigObj(self._cfgpath)
        self._cfgfile2 = None

    def addSection(self, inCategory):
        '''
        Add section to the opened ini file
        @param inCategory: the Section value
        '''
        self._cfgfile[inCategory] = {}
        self._cfgfile.write()

    def getSection(self, inCategory):
        """
        Get section all data into a dictionary
        @param inCategory: the Section value
        @return: a dictionary include all key-value pairs
        """
        return self._cfgfile[inCategory]

    def setSection(self, inCategory, inSectionValue):
        """
        Upadte a Section with another Section key/value pairs
        @param inCategory: the Section value
        @param inSectionValue: key/pairs
        """
        self.addSection(inCategory)
        self._cfgfile[inCategory].update(inSectionValue)
        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str(
                "Set section [%s] in ini file fail" % inCategory))
            logging.error(traceback.format_exc())
            pass

    def getIniVar(self, inCategory, inVarName):
        """
            Get ini Key value in Section
            @param inCategory: section name
            @param inVarName: key name
        """
        try:
            return self._cfgfile[inCategory][inVarName]
        except:
            pass
        #try to get setting from machine.ini
        try:
            return self._cfgfile2[inCategory][inVarName]
        except:
            pass
        logging.debug(str("Can't get [%s][%s] to ini file"
                          % (inCategory, inVarName)))

    def setIniVar(self, inCategory, inVarName, inVarValue):
        '''
            Write ini setting to the uniclient.ini
            @param inCategory: section name
            @param inVarName: key name
            @param inVarValue: value
        '''
        self._cfgfile[str(inCategory)][str(inVarName)] = inVarValue

        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str("Set [%s][%s] in ini file fail"
                          % (inCategory, inVarName)))
            logging.error(traceback.format_exc())

    def delIniVar(self, inCategory, inVarName):
        """
        Delete key in Section
        @param inCategory: the Section
        @param inVarName: the Key
        """
        self._cfgfile[str(inCategory)].pop(str(inVarName))
        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str("Delete [%s][%s] in ini file fail"
                              % (inCategory, inVarName)))
            logging.error(traceback.format_exc())

    def iterSection(self, inCategory):
        """
        Got the all keys in section
        @param inCategory: the Section data
        @return: the keys list
        """
        return self._cfgfile[str(inCategory)].iteritems()

if __name__ == '__main__':
    objGetIniSetting = GetIniSetting()
    objGetIniSetting.iterSection("Global")
    #objGetIniSetting.delIniVar("Global", "DebugLogFolderName")
##    objStafService = StafService()
##    objStafService.callStafService("10.201.184.65", "process", "start command cmd parms /C python util_cross_client.py md5_for_file C:\\DeployPackage\\DEPLOY.ZIP workdir C:\\CrossPlatformScript wait returnstdout returnstderr")
##    print "End"
