# Copyright (c) 2006,2007 Mitch Garnaat http://garnaat.org/
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

from xml.etree import ElementTree

class ResultSet(list):
    """
    The ResultSet is used to pass results back from the Amazon services
    to the client. It is light wrapper around Python's :py:class:`list` class,
    with some additional methods for parsing XML results from AWS. 
    Because I don't really want any dependencies on external libraries, 
    I'm using the standard SAX parser that comes with Python. The good news is 
    that it's quite fast and efficient but it makes some things rather 
    difficult.

    You can pass in, as the marker_elem parameter, a list of tuples.
    Each tuple contains a string as the first element which represents
    the XML element that the resultset needs to be on the lookout for
    and a Python class as the second element of the tuple. Each time the
    specified element is found in the XML, a new instance of the class
    will be created and popped onto the stack.

    """
    def __init__(self, marker_elem=None, marker=None):
        list.__init__(self)
        if isinstance(marker_elem, list):
            self.markers = marker_elem
        else:
            self.markers = []
        self.__marker = marker
        self.key_marker = None
        self.status = True

    @property
    def marker(self):
        return self.__marker

    def startElement(self, name, attrs, connection):
        for t in self.markers:
            if name == t[0]:
                # This is Object marker
                obj = t[1](connection)
                obj.startElement(name, attrs, connection)
                self.append(obj)
                return obj
        return None

    def to_boolean(self, value, true_value='true'):
        if value == true_value:
            return True
        else:
            return False

    def endElement(self, name, value, connection):
        if name == 'return':
            self.status = self.to_boolean(value)
        else:
            setattr(self, name, value)

    def buildElements(self):
        # enumerate all objects in list
        root = None
        if self.marker:
            root = ElementTree.Element(self.marker)
            for obj in self:
                root.append(obj.buildElements())
        
        return root


class BooleanResult(object):

    #constant
    true = 'true'
    false = 'false'

    def __init__(self, marker_elem=None):
        self.status = True
        self.request_id = None
        self.box_usage = None

    def __repr__(self):
        if self.status:
            return 'true'
        else:
            return 'false'

    def __nonzero__(self):
        return self.status

    def startElement(self, name, attrs, connection):
        return None

    def to_boolean(self, value, true_value='true'):
        if value == true_value:
            return True
        else:
            return False

    def endElement(self, name, value, connection):
        if name == 'return':
            self.status = self.to_boolean(value)
        elif name == 'StatusCode':
            self.status = self.to_boolean(value, 'Success')
        elif name == 'IsValid':
            self.status = self.to_boolean(value, 'True')
        else:
            setattr(self, name, value)

