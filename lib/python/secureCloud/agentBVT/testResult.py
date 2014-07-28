import os
import re
import time
import logging
import platform
import ConfigParser
import shutil
import subprocess
import xml
import re
import socket
import sys
from subprocess import Popen, PIPE
from urllib2 import urlopen, HTTPError, URLError
from xml.dom import minidom

import secureCloud.agentBVT.util
def  generateXmlReport(xml_patch,xml_name):

  import  xml.dom.minidom
  impl  =  xml.dom.minidom.getDOMImplementation()
  dom  =  impl.createDocument(None,  ' Result ' , None)
  root  =  dom.documentElement  
  testcase  =  dom.createElement( ' TestCase ' )
  root.appendChild(testcase)
  
  note_step = dom.createElement( ' TestStep ' )
  step_context = dom.createTextNode( ' step ' )
  note_step.appendChild(step_context)
  testcase.appendChild(note_step)
  
  note_result = dom.createElement( ' TestResut ' )
  result_context = dom.createTextNode( ' Fail ' )
  note_result.appendChild(result_context)
  testcase.appendChild(note_result)
  f =  open( xml_patch+xml_name ,  ' w ' , encoding = ' utf-8 ' )
  dom.writexml(f,  addindent = '    ' , newl = ' \n ' ,encoding = ' utf-8 ' )
  f.close()  
  return True

