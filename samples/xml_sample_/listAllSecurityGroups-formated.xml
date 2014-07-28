from xml.etree import ElementTree as ET
import urllib
import ConfigParser
import logging
import os


def checkstatus(user_scopinstallpath, checkpage):
    # Get webserviceport
    config = ConfigParser.ConfigParser()
    config.read(user_scopinstallpath)
    section_a_Value = config.get('install', 'servername')  # GET "servername"
    section_b_Value = config.get(
        'install', 'webserviceport')  # Get "webserviceport"

    OPKMSURL = "https://" + section_a_Value + ':' + section_b_Value + \
        '/' + checkpage + "/api.svc/status/"

    xmlfilename = checkpage + '.xml'
    #Download Provisioning XML file
    webfile = urllib.urlopen(OPKMSURL).read()
    fp = file(xmlfilename, 'a+')
    fp.write(webfile)
    fp.close()

    psapi = ET.parse(xmlfilename)
    ckdatabase = psapi.find('./database')
    ckencrypion = psapi.find('./encryption')
    os.remove(xmlfilename)
    if (ckdatabase.get("available") != 'true' and ckencrypion.get("available") != 'true'):
        msg = 'Cehck ' + checkpage + ' API status page fail'
        logging.error(msg)
        return -1
    else:
        msg = checkpage + ' API database = true'
        logging.info(msg)
        msg = checkpage + ' API encrypion = true'
        logging.info(msg)
        return 0
