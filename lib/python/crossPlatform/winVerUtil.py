import registryUtil
import misc


class WindowsVersion:
    '''
    Example:
    strProductName="Microsoft Windows XP"
    strCurrentVersion="5.1"
    strCurrentBuildNumber="2600"
    strBuildLab="2600.xpsp_sp3_gdr.080814-1236"
    strCSDVersion="Service Pack 3"
    '''
    strProductName = ""
    strCurrentVersion = ""
    strCurrentBuildNumber = ""
    strBuildLab = ""
    strCSDVersion = ""

    def __init__(self):
        self.load()

    def __str__(self):
        if misc.isWin64:
            return '%s(x64) %s' % (self.strProductName, self.strCSDVersion)
        else:
            return '%s %s' % (self.strProductName, self.strCSDVersion)

    def load(self):
        strProductOptionsKey = r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ProductOptions'
        obj = registryUtil.WinRegistry(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion')
        self.strProductName = obj.getValue('ProductName', '')[0]
        self.strCurrentVersion = obj.getValue('CurrentVersion', '')[0]
        self.strCurrentBuildNumber = obj.getValue('CurrentBuildNumber', '')[0]
        self.strBuildLab = obj.getValue('BuildLab', '')[0]
        self.strCSDVersion = obj.getValue('CSDVersion', '')[0]
        if self.strCurrentVersion == '5.0':
            obj = registryUtil.WinRegistry(strProductOptionsKey)
            strProductType = obj.getValue('ProductType')[0].lower()
            if strProductType == 'winnt':
                self.strProductName += ' Pro.'
            elif strProductType == 'servernt':
                self.strProductName += ' Server'
            elif strProductType == 'lanmannt':
                self.strProductName += ' Advanced Server'
        elif self.strProductName.find('Server 2003') >= 0 or self.strProductName.find('Server 2008') >= 0:
            obj = registryUtil.WinRegistry(strProductOptionsKey)
            strProductSuite = obj.getValue('ProductSuite')[0][0].lower()
            if strProductSuite == 'enterprise' and self.strProductName.lower().find('enterprise') < 0:
                self.strProductName += ' Enterprise'
            elif strProductSuite == 'terminal server':
                self.strProductName += ' Standard'


def getWindowsVersion():
    obj = WindowsVersion()
    strVersion = str(obj)
    strVersion = strVersion.replace('Microsoft', '').strip()
    strVersion = strVersion.replace('(R) ', '').strip()
    strVersion = strVersion.replace('(TM) ', '').strip()
    strVersion = strVersion.replace('Service Pack ', 'SP').strip()
    return strVersion

'''
Microsoft Windows Server 2003, Standard x64 Edition
Microsoft Windows Server 2003, Datacenter x64 Edition
Microsoft Windows Server 2003, Enterprise x64 Edition
Microsoft Windows Server 2003, Datacenter Edition for Itanium-Based Systems
Microsoft Windows Server 2003, Enterprise Edition for Itanium-based Systems
Microsoft Windows Server 2003, Standard Edition (32-bit x86)
Microsoft Windows Server 2003, Datacenter Edition (32-bit x86)
Microsoft Windows Server 2003, Enterprise Edition (32-bit x86)
Microsoft Windows Server 2003, Web Edition
Microsoft Windows XP Professional x64 Edition
Microsoft Windows XP Professional 64-Bit Edition (Itanium) 2003
Microsoft Windows XP Professional
Microsoft Windows XP Home Edition
Microsoft Windows XP Tablet PC Edition
Microsoft Windows 2000 Server
Microsoft Windows 2000 Advanced Server
Microsoft Windows 2000 Professional Edition
Microsoft Windows 2000 Datacenter Server
Windows Server 2008 for Itanium-Based Systems
Windows Server 2008 Datacenter
Windows Server 2008 Enterprise
Windows Server 2008 Standard
Windows Web Server 2008
Windows Vista Business
Windows Vista Enterprise
Windows Vista Home Basic
Windows Vista Home Premium
Windows Vista Ultimate
'''
