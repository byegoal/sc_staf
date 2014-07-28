import os
import datetime


def p4_sync(p4client, p4server, p4user, p4passwd, p4sync_path, p4zip_path, zipfile_path):

    print "p4 set ..."
    os.system("p4 set P4CLIENT=" + p4client)
    os.system("p4 set P4PORT=" + p4server)
    os.system("p4 set P4USER=" + p4user)

    print "p4 login ..."
    os.system("echo " + p4passwd + "|p4 login")

    print "Get sync source from p4"
    (stdin, p4_rtn) = os.popen2(
        "p4 sync \"" + p4sync_path + "...#head\" 2>&1")
    print "p4 sync rtn is " + p4_rtn.read()

    print "zip source by staf"
    (stdin, staf_rtn) = os.popen2("staf local zip ADD ZIPFILE " + zipfile_path + " DIRECTORY " + p4zip_path + " RECURSE RELATIVETO " + p4zip_path)
    print "staf rtn is ..."
    print staf_rtn.read()

    print "p4 logout ..."
    os.system("p4 logout")

    return staf_rtn


def main():
    p4client = "SecureCloud.Automation"
    p4server = "tw-p4proxy:1667"  # URI of p4 service
    p4user = "autouser"  # user name to access p4
    p4passwd = "AutoUser@p4v"  # password to access p4
    p4sync_path = "//DataCenter/Cloud9/Dev/Cloud9Client-2.0/Cloud9Client/QA/TMSTAF/"
    p4zip_path = "C:/p4_staf"
    str = datetime.datetime.now().strftime("mntRuby_%Y%m%d_%H%M.zip")
    zipfile_path = os.path.join("C:/TMP", str)
    p4_sync(p4client, p4server, p4user, p4passwd, p4sync_path,
            p4zip_path, zipfile_path)


if __name__ == "__main__":
    main()
