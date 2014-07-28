import os
import unittest
import ConfigParser
import logging
import tests
import sclib

logger = logging
logging.basicConfig(level=sclib.__config__.get('debug', 'level'))

