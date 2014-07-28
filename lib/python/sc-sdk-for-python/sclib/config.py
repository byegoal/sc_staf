# Copyright (c) 2012 Trend Micro, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import os
import re
import StringIO
import warnings
import ConfigParser
import sclib

os.path.expanduser('~')
expanduser = os.path.expanduser

# By default we use two locations for the securecloud configurations,
# /etc/sclib.config and ~/.sclib.config (which works on Windows and Unix).

CONFIG_FILE = '.sclib.config'
sclibConfigPath = os.path.join('/etc', CONFIG_FILE)
UserConfigPath = os.path.join(expanduser('~'), CONFIG_FILE)

sclibConfigLocations = [CONFIG_FILE]
sclibConfigLocations.append(sclibConfigPath)
sclibConfigLocations.append(UserConfigPath)

# If there's a SCLIB_CONFIG variable set, we load ONLY that variable
if 'SCLIB_CONFIG' in os.environ:
    sclibConfigLocations = [expanduser(os.environ['SCLIB_CONFIG'])]

# If there's a SCLIB_PATH variable set, we use anything there
# as the current configuration locations, split with colons
elif 'SCLIB_PATH' in os.environ:
    sclibConfigLocations = []
    for path in os.environ['sclib_PATH'].split(":"):
        sclibConfigLocations.append(expanduser(path))


class Config(ConfigParser.SafeConfigParser):

    def __init__(self, path=None, fp=None, do_load=True):
        ConfigParser.SafeConfigParser.__init__(self, {'working_dir' : '/mnt/sc', 'debug' : '0'})
        if do_load:
            if path:
                self.load_from_path(path)
            elif fp:
                self.readfp(fp)
            else:
                self.read(sclibConfigLocations)

    def load_from_path(self, path):
        file = open(path)
        for line in file.readlines():
            match = re.match("^#import[\s\t]*([^\s^\t]*)[\s\t]*$", line)
            if match:
                extended_file = match.group(1)
                (dir, file) = os.path.split(path)
                self.load_from_path(os.path.join(dir, extended_file))
        self.read(path)

    def save_option(self, path, section, option, value):
        """
        Write the specified Section.Option to the config file specified by path.
        Replace any previous value.  If the path doesn't exist, create it.
        Also add the option the the in-memory config.
        """
        config = ConfigParser.SafeConfigParser()
        config.read(path)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, value)
        fp = open(path, 'w')
        config.write(fp)
        fp.close()
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, value)

    def save_user_option(self, section, option, value):
        self.save_option(UserConfigPath, section, option, value)

    def save_system_option(self, section, option, value):
        self.save_option(sclibConfigPath, section, option, value)

    def get_value(self, section, name, default=None):
        return self.get(section, name, default)

    def get(self, section, name, default=None):
        try:
            val = ConfigParser.SafeConfigParser.get(self, section, name)
        except:
            val = default
        return val
    
    def getint(self, section, name, default=0):
        try:
            val = ConfigParser.SafeConfigParser.getint(self, section, name)
        except:
            val = int(default)
        return val
    
    def getfloat(self, section, name, default=0.0):
        try:
            val = ConfigParser.SafeConfigParser.getfloat(self, section, name)
        except:
            val = float(default)
        return val

    def getbool(self, section, name, default=False):
        if self.has_option(section, name):
            val = self.get(section, name)
            if val.lower() == 'true':
                val = True
            else:
                val = False
        else:
            val = default
        return val
    
    def setbool(self, section, name, value):
        if value:
            self.set(section, name, 'true')
        else:
            self.set(section, name, 'false')
    
    def dump(self):
        s = StringIO.StringIO()
        self.write(s)
        print s.getvalue()

    def dump_safe(self, fp=None):
        if not fp:
            fp = StringIO.StringIO()
        for section in self.sections():
            fp.write('[%s]\n' % section)
            for option in self.options(section):
                if option == 'aws_secret_access_key':
                    fp.write('%s = xxxxxxxxxxxxxxxxxx\n' % option)
                else:
                    fp.write('%s = %s\n' % (option, self.get(section, option)))
    
