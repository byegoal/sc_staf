import os
import re
import time
from urllib2 import urlopen, HTTPError, URLError
import logging
import platform
import ConfigParser
import shutil
import subprocess

def get(url, download_file, retry_count=10):

    try:
        print "downloading %s to %s" % (url, download_file)
        req = urlopen(url)
        remote_filesize = req.info().get("Content-Length")
        logging.debug("remote file size: %s" % remote_filesize)
        try:
            local_filesize = os.path.getsize(download_file)
            logging.debug("local file size: %s" % local_filesize)
            if local_filesize == local_filesize:
                logging.info("local file size equal remote file size, skip download")
                return 0
        except Exception, e:
            # if get local file size fail, keep continuing actions..
            pass

        CHUNK = 16 * 1024
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

def get_latest_build_name():
    url = "http://172.18.0.10/sc/35/daily_build_monitor.ini"
    conf = ConfigParser.ConfigParser()

    f = open("daily_build_monitor.ini", "r+")
    f.write(urlopen(url).read())
    conf.readfp(f)
    f.close()

    print conf.get("BuildVersion", "agent_win32_silent")


if __name__ == '__main__':
    script_path = os.path.dirname(os.path.realpath(__file__))
    print script_path
    get_latest_build_name()
