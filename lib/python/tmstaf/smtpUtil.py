'''
This moduel should be made refactoring to use email package instead.
Because the MimeWriter module is deprecated.
'''
import sys
import os
import base64
import cStringIO
import mimetools
import mimetypes
import MimeWriter
import re
import smtplib
import time

iso_char = re.compile('[\177-\377]', re.DOTALL)


class SmtpClient:
    '''
    This class is based on the one used in Messenger Gateway, with some modifications
    '''

    def __init__(self, strIp, intPort, strFrom, strSmtpAccount=None, strSmtpPassword=None):
        self.charset_parameters = [("charset", 'utf-8')]
        self.serverIp = strIp
        self.intPort = intPort
        self.strFrom = strFrom
        self.strSubject = ''
        self.strHtmlBody = ''
        self.strPlainBody = ''
        self.lstAttach = []

        self._server = smtplib.SMTP(strIp, intPort)
        if not strSmtpAccount:
            self._server.helo('hello')
        else:
            self._server.login(strSmtpAccount, strSmtpPassword)

    def setSubject(self, s):
        if s and iso_char.search(s):
            s = '=?utf-8?B?' + re.sub('\n', '', base64.encodestring(s)) + '?='
        self.strSubject = s

    def setBody(self, text, html=None):
        self.strPlainBody = text
        self.strHtmlBody = html

    def addAttachment(self, strFilePath, strName=None):
        if not strName:
            strName = os.path.basename(strFilePath)
        self.lstAttach.append((strName, strFilePath))

    def sendMail(self, lstTo, lstCc, strFromHeader=None):
        #convert self.to and self.cc to list type
        self._server.noop()
        strBody = self._getMailHeader(self.strSubject, lstTo,
                                      lstCc, strFromHeader) + '\n' + self._getMailBody()
        self._server.sendmail(self.strFrom, lstTo + lstCc, strBody)

    def _getMailHeader(self, strSubject, lstTo, lstCc, strFrom):
        lst = []
        if strFrom:
            lst.append('From: %s' % strFrom)
        if lstTo:
            lst.append('To: %s' % ','.join(lstTo))
        if lstCc:
            lst.append('Cc: %s' % ','.join(lstCc))
        lst.append('Date: %s' % time.strftime(
            "%a, %d %b %Y %H:%M:%S +0800", time.localtime()))
        lst.append('Subject: %s' % strSubject)
        return '\n'.join(lst)

    def _getMailBody(self):
        if not self.strPlainBody and not self.strHtmlBody and not self.lstAttach:
            return ''

        msgbody = cStringIO.StringIO()
        writer = MimeWriter.MimeWriter(msgbody)
        writer.addheader('MIME-Version', '1.0')
        writer.flushheaders()
        if self.lstAttach:
            msgbody = writer.startmultipartbody('mixed')
            msgbody.write('This is a multi-part message in MIME format.\n')
            writer.nextpart()

            mtb_body = cStringIO.StringIO()
            mtb_writer = MimeWriter.MimeWriter(mtb_body)
            self._processMimeTypeBody(mtb_writer)
            mtb_msgvalue = mtb_body.getvalue()
            mtb_body.close()

            msgbody.write(mtb_msgvalue)

            for strFileName, strFilePath in self.lstAttach:
                att_part = writer.nextpart()
                att_part.addheader('Content-Transfer-Encoding', 'base64')
                att_part.addheader('Content-Disposition', 'attachment; filename=\"' + strFileName + '\"')
                att_part.flushheaders()
                att_type = mimetypes.guess_type(strFileName)
                if att_type[0] is not None:
                    msgbody = att_part.startbody(att_type[
                        0], [('name', strFileName)])
                else:
                    msgbody = att_part.startbody('unknown',
                                                 [('name', strFileName)])
                #encode attachment
                ioBuf = cStringIO.StringIO()
                base64.encode(open(strFilePath, 'rb'), ioBuf)
                msgbody.write(ioBuf.getvalue())
                ioBuf.close()
            writer.lastpart()
        else:
            self._processMimeTypeBody(writer)

        retmsg = msgbody.getvalue()
        msgbody.close()
        return retmsg

    def _processMimeTypeBody(self, writer):
        if not self.strHtmlBody:
            body = writer.startbody('text/plain', self.charset_parameters)
            body.write(self.strPlainBody)
            return

        writer.startmultipartbody('alternative')
        part = writer.nextpart()
        part.addheader("Content-Transfer-Encoding", "quoted-printable")
        body = part.startbody('text/plain', self.charset_parameters)
        txtin = cStringIO.StringIO(self.strPlainBody)
        mimetools.encode(txtin, body, 'quoted-printable')
        txtin.close()

        part = writer.nextpart()
        part.addheader("Content-Transfer-Encoding", "quoted-printable")
        body = part.startbody('text/html', self.charset_parameters)
        htmin = cStringIO.StringIO(self.strHtmlBody)
        mimetools.encode(htmin, body, 'quoted-printable')
        htmin.close()
        writer.lastpart()

    def __del__(self):
        ''' Terminate and close SMTP session '''
        try:
            self._server.quit()
        except:
            pass
