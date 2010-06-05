# TestingConnectionBox: A set of test methods for PyQT connections
# adapted from http://www.commandprompt.com/community/pyqt/x5255
#
# Copyright (C) 2010 Cameron Neylon (C) 2000-2010 Command Prompt Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Dependencies: The application code requires PyQt and Qt to be installed. 
# The application requires the sys module from the  Python 2.6 standard 
# library. 

import sys
from PyQt4 import QtCore

class ConnectionBox(QtCore.QObject):

    def __init__(self, *args):
        apply(QtCore.QObject.__init__,(self,)+args)
        self.signalArrived=0
        self.args=[]

    def slotSlot(self, *args):
        self.signalArrived=1
        self.args=args

    def assertSignalArrived(self, signal=None):
        if  not self.signalArrived:
            raise AssertionError, ("signal %s did not arrive" % signal)

    def assertNumberOfArguments(self, number):
        if number <> len(self.args):
            raise AssertionError, \
                  ("Signal generated %i arguments, but %i were expected" %
                                    (len(self.args), number))

    def assertArgumentTypes(self, *args):
        if len(args) <> len(self.args):
            raise AssertionError, \
         ("Signal generated %i arguments, but %i were given to this function" %
                                 (len(self.args), len(args)))
        for i in range(len(args)):
            if type(self.args[0][i]) != args[i]:
                raise AssertionError, \
                      ( "Arguments don't match: %s received, should be %s." %
                                      (type(self.args[0][i]), args[i]))
