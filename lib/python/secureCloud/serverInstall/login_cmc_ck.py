import urllib
import urllib2
import cookielib
import ConfigParser


def everything_between(text, begin, end):
    idx1 = text.find(begin)
    idx2 = text.find(end, idx1)
    return text[idx1 + len(begin):idx2].strip()


def login_ck(user_scopinstallpath, adminaccount, adminpasswd):
    config = ConfigParser.ConfigParser()
    config.read(user_scopinstallpath)
    section_a_Value = config.get('install', 'servername')  # GET "servername"
    section_b_Value = config.get('install', 'cmcsslport')  # Get "cmcsslport"

    OPKMSURL = "https://" + section_a_Value + ':' + section_b_Value + \
        "/Signin.mvc/"

    cj = cookielib.CookieJar()
    prarams = (('AuthType', 'local'), ('User', adminaccount), (
        'Password', adminpasswd), ('btnSignin', 'Log on'))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2)')]
    urllib2.install_opener(opener)
    req = urllib2.Request(OPKMSURL, urllib.urlencode(prarams))
    f = urllib2.urlopen(req)
    content = f.read()
    title = everything_between(content, '<title>', '</title>')
    if title != "SecureCloud - Central Management":
        return -1
    else:
        return 0
