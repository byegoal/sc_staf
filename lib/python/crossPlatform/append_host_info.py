import logging
import subprocess
import os
import sys
import socket
import processUtil


def setNetworkHost(strHostName, strIP):
    '''
    update windows' host file
    @require:
    Windows, Linux
    @param strHostName: Ex. localhost
    @param strIP: Ex. 127.0.0.1
    @return:
        0 - success
        1 - fail
    '''
    if os.name == "nt":
        #get WINDOWS\system32\drivers\etc folder and combine host file path
        strHostFile = os.path.join(
            os.getenv("Windir"), "system32\drivers\etc\hosts")
    elif os.name == "posix":
        #linux series
        strHostFile = r"/etc/hosts"
    else:
        logging.error("OS not support yet")
        return 1

    if os.path.exists(strHostFile) == False:
        logging.error("Can't find hosts file: %s", strHostFile)
        return 1

    import fileinput
    boolExist = 0
    for line in fileinput.input(strHostFile, inplace=1):
        stripline = line.rstrip("\n").split(" ")[-1]
        if strHostName == stripline:
            #host is alreay existing, update it
            newline = str(strIP + "  " + strHostName).rstrip("\n")
            print newline
            boolExist = 1
        else:
            newline = line.rstrip("\n")
            print newline
    fileinput.close()

    if boolExist == 0:
        #host does not exist, add it
        f = open(strHostFile, "a")
        f.write(strIP + "  " + strHostName)
        f.close()

    return 0

if __name__ == '__main__':
    print '[DEBUG]' + ' '.join(sys.argv)
    if (len(sys.argv) < 2):
        print '[Error] parameter len < 2\n [USAGE]command arg1 arg2...\ncommand = setNetworkHost'
    else:
        strCommand = sys.argv[1]
        if ('setNetworkHost' == strCommand):
            try:
                strFileName, strCommand, strFileServerName, strFileServerIP = sys.argv
            except:
                print '[Error] Invalid arguments %s\n[Usage]setNetworkHost strFileServerName strFileServerIP' % sys.argv
            else:
                setNetworkHost(strFileServerName, strFileServerIP)
        else:
            print '[Error] Invalid command type\n [USAGE]command arg1 arg2...\ncommand = setNetworkHost'
