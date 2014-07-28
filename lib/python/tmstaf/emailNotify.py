"""
This module is a utility for sending email via SMTP server.
Below are some emaples:

    # setup variables
    lstTo=['somebodys_email@abc.com.tw']
    lstCc=['somebodys_email@gmail.com']
    strHtmlBodyFile='body.html'
    open(strHtmlBodyFile,'wb').write('<html><body><h1>Test</h1><hr><br>By emailNotify module</body></html>')
    strPlainBodyFile='body.txt'
    open(strPlainBodyFile,'wb').write('Test\r\nBy emailNotify module')

    #send html email
    obj=EmailNotify('TMSTAF_Admin <someadmins_email@abc.com.tw>',
        'msa.hinet.net','cpm@msa.hinet.net')
    obj.setSubject('emailNotify.EmailNotify unittest (0:22)')
    obj.setHtmlBody(strHtmlBodyFile)
    obj.send(lstTo,lstCc)

    #send plain text email
    obj=EmailNotify('TMSTAF_Admin <someadmins_email@abc.com.tw>',
        'msa.hinet.net','cpm@msa.hinet.net')
    obj.setSubject('emailNotify.EmailNotify unittest plain text(0:22)')
    obj.setPlainBody(strPlainBodyFile)
    obj.send(lstTo,lstCc)

    #send email with attachments
    obj=EmailNotify('TMSTAF_Admin <someadmins_email@abc.com.tw>')
    obj.setSubject('emailNotify.EmailNotify unittest with attachment (0:52)')
    obj.setHtmlBody(strHtmlBodyFile)
    obj.addAttachment('emailNotify.py')
    obj.addAttachment('tmstafMain.py')
    obj.send(lstTo,lstCc)
"""

import logging
import os
import subprocess


class EmailNotify:

    def __init__(self, strSender, strSmtpServer='msa.hinet.net', strFrom='cpm_automation@msa.hinet.net'):
        self._strSender = strSender  # From header
        self._strSmtpServer = strSmtpServer
        self._strFrom = strFrom  # for SMTP server
        self._strSubject = ''
        self._lstAtta = []
        self._strHtmlBodyFile = ''
        self._strPlainBodyFile = ''

    def setSubject(self, strSubject):
        self._strSubject = strSubject

    def addAttachment(self, strFilePath):
        self._lstAtta.append(strFilePath)

    def setHtmlBody(self, strFilePath):
        self._strHtmlBodyFile = strFilePath

    def setPlainBody(self, strFilePath):
        self._strPlainBodyFile = strFilePath

    def send(self, lstTo=None, lstCc=None):
        lstTo = lstTo or []
        lstCc = lstCc or []
        if not lstTo and not lstCc:
            return 0
        return self._sendBySmtpUtil(lstTo, lstCc)

    def _sendBySmtpUtil(self, lstTo, lstCc):
        from tmstaf.smtpUtil import SmtpClient
        from tmstaf.util import getException
        try:
            smtpClient = SmtpClient(self._strSmtpServer, 25, self._strFrom)
        except:
            logging.error('Exception:\n%s', getException())
            logging.error('send email to %s failed!', lstTo + lstCc)
            return 1
        smtpClient.setSubject(self._strSubject)
        if self._strPlainBodyFile:
            strPlainBody = open(self._strPlainBodyFile, 'rb').read()
        else:
            strPlainBody = 'This emil client does not support HTML cotent.'
        if self._strHtmlBodyFile:
            strHtmlBody = open(self._strHtmlBodyFile, 'rb').read()
        else:
            strHtmlBody = ''
        smtpClient.setBody(strPlainBody, strHtmlBody)
        for strFilePath in self._lstAtta:
            smtpClient.addAttachment(strFilePath)
        smtpClient.sendMail(lstTo, lstCc, self._strSender)
        return 0

    def _sendByTemail(self, lstTo, lstCc):
        temail = os.path.join(os.path.dirname(__file__), 'temail.exe')
        lstCmd = [temail, '/SMTP=%s' % self._strSmtpServer, '/B64',
                  '/HTML', '/FROM=%s' % self._strFrom]
        lstCmd.append('/HFROM=%s' % self._strSender)
        lstCmd.append('/SUBJECT=%s' % self._strSubject)
        if lstTo:
            logging.info('Send email to %s' % lstTo)
            lstCmd.append('/TO=%s' % ';'.join(lstTo))
            lstCmd.append('/HTO=%s' % ';'.join(lstTo))
        if lstCc:
            logging.info('Send email to %s' % lstCc)
            lstCmd.append('/CC=%s' % ';'.join(lstCc))
            lstCmd.append('/HCC=%s' % ';'.join(lstCc))
        if self._lstAtta:
            lstCmd.append('/ATTACH=%s' % ';'.join(self._lstAtta))
        lstCmd.append(self._strHtmlBodyFile)

        objPopen = subprocess.Popen(args=lstCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=1)
        strStdout = objPopen.stdout.read()
        intRC = objPopen.wait()
        if intRC:
            logging.info('CMD= %s', ' '.join(lstCmd))
            logging.info('temail.exe return: %s', intRC)
            if strStdout:
                logging.info(strStdout)
        else:
            logging.debug('temail.exe return: %s', intRC)
            if strStdout:
                logging.debug(strStdout)
        return intRC
