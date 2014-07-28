import ConfigParser
from tmstaf.util import upgradeIniFile


class ProductSetting(object):

    def __init__(self):
        self._dic = {}

    def loadFromIni(self, strIniFile):
        c = ConfigParser.ConfigParser()
        c.optionxform = str  # option name will be "case sensitive"
        c.read(strIniFile)
        for strSection in c.sections():
            for strOption in c.options(strSection):
                self._dic['%s.%s' % (strSection, strOption)
                          ] = c.get(strSection, strOption).strip()

    def get(self, strKey, default=None):
        if default is not None:
            return self._dic.get(strKey, default)
        return self._dic[strKey]

    def hasKey(self, strKey):
        return strKey in self._dic

    def set(self, strKey, strValue):
        self._dic[strKey] = strValue


def updateNewVersion(strTemplatePath, strCurrentPath):
    return upgradeIniFile(strTemplatePath, strCurrentPath)
