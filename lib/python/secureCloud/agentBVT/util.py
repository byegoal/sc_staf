import ConfigParser
import logging
import subprocess
from urllib2 import urlopen, HTTPError, URLError
from __builtin__ import file

def python_include(include_file):
    s = open(include_file).read()
    exec s
    return 0


def config(config_path):
    c = ConfigParser.SafeConfigParser()
    c.read(config_path)
    d = {}

    for cat in c.sections():
        d[cat] = {}
        for key, val in c.items(cat):
            d[cat][key] = val

    return d


def windows_ntp_sync():
    command = """ w32tm /resync """
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:")
    logging.info(return_code)

    return return_code

	
	
def get(url, download_file, retry_count=10):
    try:
        logging.info( "downloading %s to %s" % (url, download_file) )
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

        #if platform.system() == "Windows":
        #    download_dir = r"c:\tmp"
        #else:
        #    download_dir = r"/tmp"

        #if not os.path.exists(download_dir):
        #    os.makedirs(download_dir)
        #    print "tmp folder created"

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
    
def get_file_first_line(path):
    file = open(path,'r')
    return file.readline()

def get_file_lines(path):
    file = open(path,'r')
    return file.readlines()
    
def gen_config_file(file_name,msg):
    f = open(file_name, "w")
    f.write(msg)
    f.close()