import logging
import os
import crossPlatform.processUtil
import ConfigParser


def autoinstall(config_path, installer_path):
    STR_AUTOINSTALLER_EXE = os.path.join(
        os.path.dirname(__file__) or os.getcwd(), 'autoinstaller_win.exe')
    #STR_AUTOINSTALLER_CFG=os.path.join(os.path.dirname(__file__) or os.getcwd(),'scopinstall.ini')
    STR_AUTOINSTALLER_CFG = config_path
    STR_USED_AUTOINSTALLER_CFG = os.path.join(
        os.path.dirname(config_path), 'used_scopinstall.ini')
    STR_LOG = os.path.join(os.path.dirname(config_path), 'log.txt')
    config = ConfigParser.ConfigParser()
    config.read(STR_AUTOINSTALLER_CFG)
    config.set("install", "Excutelocation", "Msiexec.exe /i " +
               installer_path + " /l*v " + STR_LOG)
    with open(STR_USED_AUTOINSTALLER_CFG, 'wb') as configfile:
        config.write(configfile)
    lstCmd = [STR_AUTOINSTALLER_EXE, STR_USED_AUTOINSTALLER_CFG]
    logging.debug("autoinstaller: %s", lstCmd)
    logging.info('Start to install')
    objP = crossPlatform.processUtil.TmProcess(lstCmd)
    strStdout = objP.readStdout()
    intRc = objP.wait()
    #os.system(STR_AUTOINSTALLER_EXE+' '+STR_AUTOINSTALLER_CFG)
    logging.info("Installed with return: %s", intRc)
    print strStdout
    return intRc


def main():
    import sys
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    args = sys.argv[1:]
    logging.info(args)
    autoinstall(args[0], args[1])

if __name__ == '__main__':
    main()
