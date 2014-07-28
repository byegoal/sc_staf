# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
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

from sclib.config import Config, sclibConfigLocations

import os
import platform
import re
import sys
import logging
import logging.config
import urlparse

__module__ = 'sclib'

__version__ = '3.5.1000'
Version = __version__  # for backward compatibility

__config__ = Config()
UserAgent = '%s/%s (%s)' % (__module__, __version__, sys.platform)

def init_logging():
    for file in sclibConfigLocations:
        try:
            logging.config.fileConfig(os.path.expanduser(Config))
        except:
            pass


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger(__module__)
perflog = logging.getLogger('%s.perf' % (__module__))
log.addHandler(NullHandler())
perflog.addHandler(NullHandler())
init_logging()

# convenience function to set logging to a particular file


def set_file_logger(name, filepath, level=logging.INFO, format_string=None):
    global log
    if not format_string:
        format_string = "%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(filepath)
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger


def set_stream_logger(name, level=logging.DEBUG, format_string=None):
    global log
    if not format_string:
        format_string = "%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.StreamHandler()
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger

def connect_sc(sc_host_url, sc_broker, sc_broker_key):
    """
    :type sc_host_url: string
    :param sc_host_url: Your SecureCloud broker url. Ex. https://ms.securecloud.com:7443/broker/API.svc/v3.5

    :type sc_broker: string
    :param sc_broker: Your broker name
    
    :type sc_broker_key: string
    :param sc_broker_key: Your broker access key

    :rtype: :class:`sclib.sc.connection.SCConnection`
    :return: A connection to SecureCloud
    """
    from sclib.sc.connection import SCConnection
    return SCConnection( sc_host_url, 
                         sc_broker, 
                         sc_broker_key )
