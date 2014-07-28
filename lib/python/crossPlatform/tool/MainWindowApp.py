""" Handle the main application window """
# $Id: MainWindowApp.py,v 1.3 2004/04/12 04:46:16 prof Exp $
import Tkinter
import logging
import ViewLog
import ThreadsConnector
import ActionWindow
import ActionWindow2
import app2
import app3
import tkFileDialog
import gettext
_ = gettext.gettext


def getMachineInfo(strMachineFile='Machine_List.ini', oMachineIni=None):
    '''
        Get machine information
        @param strMachineFile: the machine config file name
        @param oMachineIni: the machine ini object default is None, otherwise
                            ignore strMachineFile use this object get machine
                            list information.
        @return:
        A tuple (dictMachineInfo,mapMachinePlatform)
        dictMachineInfo - A Dictionary contains {machineIP :
        [machineName,machineArchitecture,machinePlatform]}
        mapMachinePlatform - A dictionary contains {machineName : Platform}
    '''
##    if oMachineIni == None:
##        if cp_ini.g_objIni == None:
##            machineListObj = crossPlatform.util.GetIniSetting(strMachineFile)
##        else:
##            machineListObj = cp_ini.g_objIni
##    else:
##        machineListObj = oMachineIni

    from utility import GetIniSetting
    machineListObj = GetIniSetting(strMachineFile)
    dictMachineInfo = {}
    mapMachinePlatform = {}
    listMachineName = []
    listMachineID = []
    try:
        dictMachine = dict(machineListObj.iterSection('TestingTarget'))
        for strKey in dictMachine:
            listOneMachineInfo = dictMachine[strKey]

            if None == listOneMachineInfo:
                break
            else:
                dictMachineInfo[listOneMachineInfo[0]] = listOneMachineInfo[1:]
                listMachineName.append(listOneMachineInfo[1])
                mapMachinePlatform[listOneMachineInfo[1]
                                   ] = listOneMachineInfo[3]
                listMachineID.append(listOneMachineInfo[4])
    except:
        pass
    return (dictMachineInfo, mapMachinePlatform, listMachineID)


class MainWindowApp:

    def __init__(self, log):
        """ Remember cumulative log, get logger """
        self.log = log
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialdir = "C:\\"
        self.machinelist = []

    def run(self):
        """ Create and run GUI """
        self.root = root = Tkinter.Tk()
        root.title(_('Monitor Client Status'))
        #Tkinter.Button(root, text=_('Start'), command=self.onStart, width=10).pack(side=Tkinter.LEFT)
        #Tkinter.Button(root, text=_('View Log'), command=self.onViewLog, width=10).pack(side=Tkinter.LEFT)
        #Tkinter.Button(root, text=_(''), width=1).pack(side=Tkinter.LEFT)
        Tkinter.Button(root, text=_('Monitor'),
                       command=self.onMonitor, width=10).pack(side=Tkinter.LEFT)
        #Tkinter.Button(root, text=_('Browse'), command=self.onBrowse, width=10).pack(side=Tkinter.LEFT)
        Tkinter.Button(root, text=_(''), width=1).pack(side=Tkinter.LEFT)
        Tkinter.Button(root, text=_('Exit'), command=self.onExit,
                       width=10).pack(side=Tkinter.LEFT)
        root.mainloop()

    def onExit(self):
        """ Process 'Exit' command """
        self.root.quit()

    def onViewLog(self):
        """ Process 'View Log' command """
        ViewLog.ViewLog(self.root, self.log)

    def onStart(self):
        """ Process 'Start' command """
        self.logger.info(_('Preparing and starting calculations'))
        conn = ThreadsConnector.ThreadsConnector()
        wnd = ActionWindow.ActionWindow(self.root, _('Countdown Calculations'),
                                        _('Counting down from 100 to 1'))
        conn.runInGui(wnd, conn, None, app2.calc, 'calc')

    def onMonitor(self):
        """ Process 'Monitor' command """
        self.logger.info(
            _('Preparing and starting Monitor Machine Status View'))
        if len(self.machinelist) == 0:
            self.onBrowse()
        if len(self.machinelist) > 0:
            conn = ThreadsConnector.ThreadsConnector()
            wnd = ActionWindow2.ActionWindow(self.root, _('Test Machine Status View'), _('List all test machine status'), self.machinelist)
            conn.runInGui(wnd, conn, None, app3.monitor,
                          'monitor', self.machinelist)

    def onBrowse(self):
        """ Process 'onBrowse' command """
        self.logger.info(_('Preparing and starting Test Machine Status View'))
        fullfilename = ''
        fullfilename = tkFileDialog.askopenfilename(parent=self.root, defaultextension="ini", initialdir=self.initialdir, title="look machine list file")
        if (fullfilename is not None) and (fullfilename != ''):
            import os
            (path, name) = os.path.split(fullfilename)
            self.initialdir = path
            try:
                dictMachineInfo, mapMachinePlatform, listMachineID = getMachineInfo(fullfilename)
                if dictMachineInfo is not None:
                    self.machinelist = []
                    for item in dictMachineInfo:
                        self.machinelist.append(item)
                    self.machinelist.sort()
            except:
                pass

if __name__ == '__main__':
    self.machinelist = []
    dictMachineInfo, mapMachinePlatform, listMachineID = getMachineInfo(
        "C:\\STAF\\testsuites\\VIZOR_OEM\\OEM_ASUS_Machine_List.ini")
    if dictMachineInfo is not None:
        for item in dictMachineInfo:
            list.append(item)
        list.sort()
    print list
    print "End"
