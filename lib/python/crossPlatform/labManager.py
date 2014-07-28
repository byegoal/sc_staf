"""
The Lab Manager utility module
"""
import httplib

##from xml.sax import make_parser, SAXException
##from xml.sax.handler import feature_namespaces
import logging


def funcListConfigurations(strLmIp="10.201.16.10"):
    """
    To list Lab Manager Configuration
    @type strLmIp: the Lab Manager IP
    """
    logging.info('LabManger >> funcListConfigurations')

    strSoapTemplate = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:lab="http://vmware.com/labmanager">
   <soap:Header>
      <lab:AuthenticationHeader>
         <!--Optional:-->
         <lab:username>Titanium_auto</lab:username>
         <!--Optional:-->
         <lab:password>Titanium@2009</lab:password>
         <!--Optional:-->
         <lab:organizationname></lab:organizationname>
      </lab:AuthenticationHeader>
   </soap:Header>
   <soap:Body>
      <lab:funcListConfigurations>
         <lab:configurationType>1</lab:configurationType>
      </lab:funcListConfigurations>
   </soap:Body>
</soap:Envelope>"""

    logging.info('LabManger >> funcListConfigurations >> SoapMessage:')
    logging.info(strSoapTemplate)

    #print SoapMessage
    webservice = httplib.HTTPS(strLmIp)
    webservice.putrequest("POST", "/LabManager/SOAP/LabManager.asmx")
    webservice.putheader("Host", strLmIp)
    webservice.putheader("User-Agent", "Python Post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(strSoapTemplate))
    webservice.putheader("SOAPAction",
                         "\"http://vmware.com/labmanager/funcListConfigurations\"")
    webservice.endheaders()
    webservice.send(strSoapTemplate)

    # get the response

    logging.info('LabManger >> funcListConfigurations >> Get response:')
    lstReplyHeader = webservice.getreply()
    logging.info(lstReplyHeader)

    logging.info('LabManger >> funcListConfigurations >> Get file:')
    objReplyContent = webservice.getfile()
    logging.info(objReplyContent.next())


def funcGetMachineId(strVmName, strLmIp="10.201.16.10"):
    """
    To get lab manager machine id for operation.
    """
    strSoapTemplate1 = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:lab="http://vmware.com/labmanager">
   <soap:Header>
      <lab:AuthenticationHeader>
         <!--Optional:-->
         <lab:username>Titanium_auto</lab:username>
         <!--Optional:-->
         <lab:password>Titanium@2009</lab:password>
         <!--Optional:-->
         <lab:organizationname></lab:organizationname>
      </lab:AuthenticationHeader>
   </soap:Header>
   <soap:Body>
      <lab:GetMachineByName>
         <lab:configurationId>989</lab:configurationId>
         <lab:name>%s</lab:name>
      </lab:GetMachineByName>
   </soap:Body>
</soap:Envelope>"""

    logging.info('LabManger >> funcListConfigurations >> SoapMessage:')
    strSoapTemplate1 = strSoapTemplate1 % (strVmName)
    logging.info(strSoapTemplate1)

    #print SoapMessage
    webservice = httplib.HTTPS(strLmIp)
    webservice.putrequest("POST", "/LabManager/SOAP/LabManager.asmx")
    webservice.putheader("Host", strLmIp)
    webservice.putheader("User-Agent", "Python Post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(strSoapTemplate1))
    webservice.putheader(
        "SOAPAction", "\"http://vmware.com/labmanager/GetMachineByName\"")
    webservice.endheaders()
    webservice.send(strSoapTemplate1)

    # get the response

    logging.info('LabManger >> funcListConfigurations >> Get response:')
    lstReplyHeader = webservice.getreply()
    logging.info(lstReplyHeader)

    if lstReplyHeader[1] == 'OK':
        logging.info('LabManger >> funcListConfigurations >> Get file:')
        objReplyContent = webservice.getfile()
        logging.info(objReplyContent.next())

#===============================================================================
# 1 XPower On. Turns on a machine.
# 2 XPower Off. Turns off a machine. Nothing is saved.
# 3 XSuspend. Freezes a machine CPU and state.
# 4 XResume. Resumes a suspended machine.
# 5 XReset. Reboots a machine.
# 6 XSnapshot. Save a machine state at a specific point in time.
# 7 XRevert. Returns a machine to a snapshot state.
# 8 XShutdown. Shuts down a machine before turning off.
#===============================================================================


def funcMachineActionTemplate(intMachineID, intActionID,
                              strLmIp="10.201.16.10",
                              strLmUserName="Titanium_auto",
                              strLmPassword="Titanium@2009"):
    """
    Do lab manager action by input machine id and action id
    @type strLmIp: String
    @param strLmIp: the Lab Manager IP
    @type strLmUserName: String
    @param strLmUserName: the Lab Manager User Account
    @type strLmPassword: String
    @param strLmPassword: the Lab Manager User Password
    @return: the Lab Manager execute result code. For example 200 means OK
    """
    logging.info('LabManger >> funcMachinePerformActionTemplate')
    logMessage = 'intMachineID=%d, intActionID=%d' % (
        intMachineID, intActionID)
    logging.info(logMessage)

    strSoapTemplate = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:lab="http://vmware.com/labmanager">
   <soapenv:Header>
      <lab:AuthenticationHeader>
         <!--Optional:-->
         <lab:username>%s</lab:username>
         <!--Optional:-->
         <lab:password>%s</lab:password>
         <!--Optional:-->
         <lab:organizationname></lab:organizationname>
      </lab:AuthenticationHeader>
   </soapenv:Header>
   <soapenv:Body>
      <lab:MachinePerformAction>
         <lab:machineId>%d</lab:machineId>
         <lab:action>%d</lab:action>
      </lab:MachinePerformAction>
   </soapenv:Body>
</soapenv:Envelope>"""

    strSoapMessage = strSoapTemplate % (strLmUserName, strLmPassword,
                                        intMachineID, intActionID)

    logging.info('LabManger >> funcMachinePerformActionTemplate'
                 ' >> SoapMessage:')
    logging.info(strSoapMessage)

    #print SoapMessage
    webservice = httplib.HTTPS(strLmIp)
    webservice.putrequest("POST", "/LabManager/SOAP/LabManager.asmx")
    webservice.putheader("Host", strLmIp)
    webservice.putheader("User-Agent", "Python Post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(strSoapMessage))
    webservice.putheader("SOAPAction",
                         "\"http://vmware.com/labmanager/MachinePerformAction\"")
    webservice.endheaders()
    webservice.send(strSoapMessage)

    # get the response

    logging.info('LabManger >> funcMachinePerformActionTemplate >>'
                 ' Get response:')
    lstReplyHeader = webservice.getreply()
    logging.info(lstReplyHeader)
    return lstReplyHeader[0]

#===============================================================================
# 1 XPower On. Turns on a machine.
# 2 XPower Off. Turns off a machine. Nothing is saved.
# 3 XSuspend. Freezes a machine CPU and state.
# 4 XResume. Resumes a suspended machine.
# 5 XReset. Reboots a machine.
# 6 XSnapshot. Save a machine state at a specific point in time.
# 7 XRevert. Returns a machine to a snapshot state.
# 8 XShutdown. Shuts down a machine before turning off.
#===============================================================================


def funcPowerOn(intMachineID):
    """
    Do power on
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 1)


def funcPowerOff(intMachineID):
    """
    Do power off
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 2)


def funcSuspend(intMachineID):
    """
    Do suspend
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 3)


def funcResume(intMachineID):
    """
    Do resume
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 4)


def funcReset(intMachineID):
    """
    Do reset
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 5)


def funcSnapshot(intMachineID):
    """
    Do snapshot
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 6)


def funcRevert(intMachineID, strLmIp, strLmUserName, strLmPassword):
    """
    Do revert Lab Manager VM
    @type intMachineID: Integer
    @param intMachineID: the VM id for identify action target
    @type strLmIp: String
    @param strLmIp: the Lab Manager IP
    @type strLmUserName: String
    @param strLmUserName: the Lab Manager User Account
    @type strLmPassword: String
    @param strLmPassword: the Lab Manager User Password
    @return: the Lab Manager execute result message
    """
    return funcMachineActionTemplate(intMachineID, 7, strLmIp, strLmUserName, strLmPassword)


def funcShutdown(intMachineID):
    """
    Do shutdown
    @param intMachineID: machine id
    """
    return funcMachineActionTemplate(intMachineID, 8)

#===============================================================================
#Machine1 = 10.201.173.211,Ti_STAF_V322,x86,Vista SP2,1931
#Machine2 = 10.201.173.212,Ti_STAF_XP,x86,XP Professional SP3,1894
#Machine3 = 10.201.173.213,Ti_STAF_V641,x64,Vista SP1,1996
if __name__ == '__main__':
    #funcListConfigurations()
    #funcGetMachineId('VaHPS264_RU')
    funcRevert(2624)
    ##Reset(1894)
    ##time.sleep(60)
    ##Revert(1894)
    ##Reset(1931)
    ##time.sleep(60)
    ##Revert(1931)
    #Reset(2010)
    #time.sleep(60)
    #Revert(2010)
    #Snapshot(1996)
    #Reset(1996)
    #time.sleep(60)
    #Revert(1996)
    #Snapshot(1996)
#===============================================================================
