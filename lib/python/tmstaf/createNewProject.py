import os
import shutil
import tmstaf.iniparse

MODULE_PATH = os.path.dirname(__file__) or os.getcwd()


def main():
    print 'TMSTAF Project Wizard'
    while 1:
        strProjectPath = raw_input(
            'Specify the full path for the new project:')
        if not strProjectPath:
            continue
        if os.path.exists(strProjectPath):
            print '"%s" already exists!' % strProjectPath
        else:
            break
    while 1:
        strProjectName = raw_input('Specify the project name:')
        if strProjectName:
            break
    os.makedirs(strProjectPath)
    # Copy files
    strIniFile = os.path.join(strProjectPath, 'tmstaf.ini')
    shutil.copy(os.path.join(MODULE_PATH, 'tmstaf.ini.template'), strIniFile)
    shutil.copy(os.path.join(MODULE_PATH, 'run.bat'), strProjectPath)
    # Modify tmstaf.ini
    cfg = tmstaf.iniparse.INIConfig(file(strIniFile), optionxformvalue=None)
    cfg.TestwareConfig.ProductName = strProjectName
    cfg.TestwareConfig.TestCaseRootFolder = strProjectPath
    cfg.TestwareConfig.TestResultFolder = os.path.join(
        '%(TestCaseRootFolder)s', 'result')
    f = open(strIniFile, 'wb')
    f.write(str(cfg))
    f.close()
    print 'New project "%s" is created in "%s"' % (
        strProjectName, strProjectPath)

if __name__ == '__main__':
    main()
