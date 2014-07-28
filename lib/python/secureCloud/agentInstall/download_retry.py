import os
import time
from urllib2 import urlopen, HTTPError, URLError
import logging
import platform


def get(url, download_file, retry_count=10):
    try:
        print "start download %s to %s" % (url, download_file)
        req = urlopen(url)
        CHUNK = 16 * 1024
        if platform.system() == "Windows":
            if not os.path.exists("c:\\tmp"):
                os.makedirs("c:\\tmp")
                print "tmp folder created"
        else:
            if not os.path.exists("\\tmp"):
                os.makedirs("\\tmp")

        fp = open(download_file, 'wb')
        while True:
            chunk = req.read(CHUNK)
            if not chunk:
                break
            fp.write(chunk)
        fp.close()
        return 0

    except HTTPError, e:
        logging.error("download build fail HTTPError: " + str(
            e.code) + " " + url)
        return -1

    except URLError, e:
        print "URLError: ", e.reason, url
        logging.error("download build fail URLError: " + str(
            e.reason) + " " + url)
        logging.error("URLError: " + e.reason + " " + url)
        return -1

if __name__ == '__main__':
    get("http://211.76.133.181/sc/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.ex", "latest_build.exe")
    get("http://211.76.133.181/sc/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.exe", "latest_build.exe")
    #get("http://dl.dropbox.com/u/60937902/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.exe", "latest_build.exe")
