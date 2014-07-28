import os

ets = r'\\tw-ets-fs.tw.trendnet.org'
c9_build = r'\\172.18.0.10'
share_name = 'cloud9user'
share_pass = 'P@ssw0rd'

#os.system("NET USE %s" % ets)
#os.system("NET USE %s %s /USER:%s" % (c9_build, share_pass, share_name))
os.system("NET USE")