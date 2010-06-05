# LaBLog Poster: A desktop App for interacting with the University of 
# Southampton LaBLog system as an electronic laboratory notebook
#
# Copyright (C) 2010 Cameron Neylon
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
# The desktopAppDoc module utilises the lablogpost module available with
# this source distribution and separately with a ccZero public domain
# waiver at ####. The application requires a range of modules from the 
# Python 2.6 standard library. 

import sys
import os.path
import unittest
import logging
import lablogpost
from PyQt4.QtCore import *

class MultiPostDoc(QObject):
    """Document for a multi-post directory data upload

    Document model class that describes the information for the 
    posting of a directory of data files as a set of blog posts.
    Includes information on the possible blog server, selected 
    blog server, the target blog housed on that server, as well as
    possible usernames, selected usernames, post content, post 
    title, whether to use the filenames as post titles, and the
    local path to the target directory"""

    def __init__(self, *args):
        QObject.__init__(self, *args)

        self.initBlogServerList()
        self.initCurrentBlogServer()
        self.initServertoBlogMapping()
        self.initCurrentUsername()
        self.initCurrentBlog()

        self.initPostTitle()
        self.initUseFilename()
        self.initPostContent()

        self.initDataDirectory()
        self.status = []



    def initBlogServerList(self):
        self.blogserverlist = ['http://biolab.isis.rl.ac.uk',
                               'http://blogs.chem.soton.ac.uk',
                               'http://blog_dev.sidious.chem.soton.ac.uk']

    def initCurrentBlogServer(self):
        self.currentblogserver = 'http://biolab.isis.rl.ac.uk'

    def initServertoBlogMapping(self):
        self.servertoblogmapping = {
          'http://biolab.isis.rl.ac.uk'   : 
              ["testing_sandpit", "camerons_labblog", "Lab Materials Login"],
          'http://blogs.chem.soton.ac.uk' : 
              ["frey_group", "bio_sandpit"],
          'http://blog_dev.sidious.chem.soton.ac.uk' :
              ["frey_group", "bio_sandpit"]
                          }

    def setCurrentBlogServer(self, index):
        #self.currentblogserver = self.blogserverlist[index]
        try:
            assert type(index) == int, 'List indices must be an integer'
            assert index < len(self.blogserverlist
                               ), 'List index out of range'
            self.currentblogserver = \
                       self.blogserverlist[index]
            self.emit(SIGNAL('sigDocCurrentBlogServerSet'), 
                            (self.currentblogserver,))

            self.status.append('Blog server set to: ' + self.currentblogserver)
            self.emit(SIGNAL('sigDocUpdateStatusBar'))

            return True

        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False


    def getCurrentBlogServer(self):
        return self.currentblogserver

    def getBlogsforCurrentBlogServer(self):        
        return self.servertoblogmapping[self.currentblogserver]

    def initCurrentBlog(self):
        self.currentblog = self.getBlogsforCurrentBlogServer()[0]

    def setCurrentBlog(self, index):
        try:
            assert type(index) == int, 'List indices must be an integer'
            assert index < len(self.getBlogsforCurrentBlogServer()
                               ), 'List index out of range'
            self.currentblog = self.getBlogsforCurrentBlogServer()[index]
            self.emit(SIGNAL('sigDocCurrentBlogSet'), (self.currentblog,))

            self.status.append('Blog set to: ' + self.currentblog)
            self.emit(SIGNAL('sigDocUpdateStatusBar'))

            return True

        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getCurrentBlog(self):
        return self.currentblog

    def getUsernamesforCurrentBlogServer(self):
        self.usernamemapping = {
            'http://biolab.isis.rl.ac.uk'   : ['cameronneylon.net',
                                              'cameron.neylon.myopenid.com',
                                               ],
            'http://blogs.chem.soton.ac.uk' : ['dcn', 'ajm3'],
            'http://blog_dev.sidious.chem.soton.ac.uk' : ['dcn', 'ajm3']
                          }
        return self.usernamemapping[self.currentblogserver]

    def initCurrentUsername(self):
        self.currentusername = self.getUsernamesforCurrentBlogServer()[0]

    def setCurrentUsername(self, index):
        try:
            assert type(index) == int, 'List indices must be an integer'
            assert index < len(self.getUsernamesforCurrentBlogServer()
                               ), 'List index out of range'
            self.currentusername = \
                self.getUsernamesforCurrentBlogServer()[index]
            self.emit(SIGNAL('sigDocCurrentUsernameSet'), 
                                        (self.currentusername,))
            self.status.append('Username set to: ' + self.currentusername)
            self.emit(SIGNAL('sigDocUpdateStatusBar'))

            return True

        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getCurrentUsername(self):
        return self.currentusername

    def initPostTitle(self):
        self.posttitle = ''

    def setPostTitle(self, string):
        logging.debug('Set Post Title: Received: ' + string)
        try:
            assert type(string) == QString, \
                               'Post title must be a string'
            self.posttitle = string
            self.emit(SIGNAL('sigDocPostTitleSet'), (self.posttitle,))
            return True
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getPostTitle(self):
        return self.posttitle

    def initUseFilename(self):
        self.usefilename = False

    def setUseFilename(self, boolean):
        try:
            assert type(boolean) == bool, 'UseFileName must be True or False'
            self.usefilename = boolean
            self.emit(SIGNAL('sigDocUseFilenameChanged'), (self.usefilename,))
            return True

        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getUseFilename(self):
        return self.usefilename

    def initPostContent(self):
        self.postcontent = ''

    def setPostContent(self, string):
        logging.debug('Set Post Content: Received: ' + string)
        try:
            assert type(string) == QString, \
                                      'Post content must be a string'
            self.postcontent = string
            self.emit(SIGNAL('sigDocPostContentChanged'), (self.postcontent,))
            return True
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getPostContent(self):
        return self.postcontent

    def initDataDirectory(self):
        self.datadirectory = ''
        
    def setDataDirectory(self, string):
        try:
            assert type(string) == QString, \
                                        'Data directory must be a string'
            self.datadirectory = str(string)
            self.emit(SIGNAL('sigDocDataDirectoryChanged'), 
                            (self.datadirectory,))
            return True
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getDataDirectory(self):
        return self.datadirectory


########################################
#
# Data Upload Methods and additional gumpf
#
########################################

    def doMultiPostDataUpload(self):
        """Method for passing parameters to directory upload methods"""

        # Check that required information is available
        try:
            assert ((self.posttitle != '') or 
                    (self.usefilename == True)), 'Need post title'
            assert self.postcontent != '', 'Need post text'
            assert self.datadirectory != '', 'No directory selected'
            assert os.path.exists(self.datadirectory), \
                    'The path appears not to exist'
        
        # If insufficient information is available raise a warning dialog
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

        self.status.append('Sending data posts to server')
        self.emit(SIGNAL('sigDocUpdateStatusBar'))
        self.emit(SIGNAL('sigDocMultiPostDataUploading'))
       
        self.filelist = []
        for file in os.listdir(self.datadirectory):
            self.filelist.append(os.path.join(self.datadirectory, file))

        posts = lablogpost.MultiDataFileUpload(
                **{'filelist'   : self.filelist,
                   'postnames'  : str(self.posttitle),
                   'posttext'   : str(self.postcontent),
                   'metadata'   : {'key1':'value1'},
                   'server_url' : str(self.currentblogserver),
                   'blog_sname' : str(self.currentblog),
                   'username'   : str(self.currentusername),
                   'section'    : 'API Testing',
                   'uid'        : lablogpost.DEFAULT_UID
                   })

        self.data_fail, self.post_fail, self.length = posts.doUpload()
        self.emit(SIGNAL('sigDocFinishedUploading'))

        self.status.append('Uploaded ' + str(self.length) + ' data objects')

        

###############################################################
#
# UnitTests
#
################################################################
class AbstractTestCase(unittest.TestCase):
    """An abstract test case that contains all the setup variables"""

    def setUp(self):
        self.doc = MultiPostDoc()
        self.connectionBox = ConnectionBox()
        self.types = [int, str, bool]
        self.testint = 1
        self.teststring = 'a test string'
        self.testbool = True
        self.testparams = [self.testint, self.teststring, self.testbool]
        self.doc = MultiPostDoc()

        self.signals = [{'signal'     : 'sigDocCurrentBlogServerSet',
                         'function'   : self.doc.setCurrentBlogServer,
                         'getmethod'  : self.doc.getCurrentBlogServer,
                         'funcparams' : 1,
                         'testparam'  : [self.testint],
                         'returnexp'  : 'http://blogs.chem.soton.ac.uk',
                         'funcptype'  : int,
                         'returnspar' : 1,
                         'returntype' : str},

                        {'signal'     : 'sigDocCurrentBlogSet',
                         'function'   : self.doc.setCurrentBlog,
                         'getmethod'  : self.doc.getCurrentBlog,
                         'funcparams' : 1,
                         'testparam'  : [0],
                         'returnexp'  : 'camerons_labblog',
                         'funcptype'  : int,
                         'returnspar' : 1,
                         'returntype' : str},

                        {'signal'     : 'sigDocCurrentUsernameSet',
                         'function'   : self.doc.setCurrentUsername,
                         'getmethod'  : self.doc.getCurrentUsername,
                         'funcparams' : 1,
                         'testparam'  : [0],
                         'returnexp'  : 'cameron.neylon.myopenid.com',
                         'funcptype'  : int,
                         'returnspar' : 1,
                         'returntype' : str},

                        {'signal'     : 'sigDocPostTitleSet',
                         'function'   : self.doc.setPostTitle,
                         'getmethod'  : self.doc.getPostTitle,
                         'funcparams' : 1,
                         'testparam'  : ['test_title'],
                         'funcptype'  : str,
                         'returnexp'  : self.teststring,
                         'returnspar' : 1,
                         'returntype' : str},

                        {'signal'     : 'sigDocUseFilenameChanged',
                         'function'   : self.doc.setUseFilename,
                         'getmethod'  : self.doc.getUseFilename,
                         'funcparams' : 1,
                         'testparam'  : [True],
                         'returnexp'  : self.testbool,
                         'funcptype'  : bool,
                         'returnspar' : 1,
                         'returntype' : bool},

                        {'signal'     : 'sigDocPostContentChanged',
                         'function'   : self.doc.setPostContent,
                         'getmethod'  : self.doc.getPostContent,
                         'funcparams' : 1,
                         'testparam'  : ['some text content'],
                         'returnexp'  : self.teststring,
                         'funcptype'  : str,
                         'returnspar' : 1,
                         'returntype' : str},

                        {'signal'     : 'sigDocDataDirectoryChanged',
                         'function'   : self.doc.setDataDirectory,
                         'getmethod'  : self.doc.getDataDirectory,
                         'funcparams' : 1,
                         'testparam'  : ['some string'],
                         'returnexp'  : self.teststring,
                         'funcptype'  : str,
                         'returnspar' : 1,
                         'returntype' : str}
                        ] 

    def tearDown(self):
        self.doc = None
        self.connectionBox = None

class InitTestCase(unittest.TestCase):
    """Check that documents initialize properly
    """

    def checkInitialisation(self):
        """Check that documents initialize properly as expected
        """

        self.doc = MultiPostDoc()

        self.assertEqual(self.doc.blogserverlist, [
                               'http://biolab.isis.rl.ac.uk',
                               'http://blogs.chem.soton.ac.uk',
                               'http://blog_dev.sidious.chem.soton.ac.uk'])
        self.assertEqual(self.doc.currentblogserver, 
                               'http://biolab.isis.rl.ac.uk')
        self.assertEqual(self.doc.currentblog, 'testing_sandpit')
        self.assertEqual(self.doc.currentusername, 'cameronneylon.net')
        self.assertEqual(self.doc.posttitle, '')
        self.assertEqual(self.doc.usefilename, False)
        self.assertEqual(self.doc.postcontent, '')

class ErrorCatchingTestCase(AbstractTestCase):
    """Check that all set functions fire errors as expected
    """


    def checkErrors(self):
        """Test case that tries all parameters against all functions

        The test case loops over each of the functions registered and
        then within each function calls the set Function with the
        registered test parameters of each type. For the incorrect
        parameter types it checks that the error catching method is
        triggered, that the correct error message is provided, and that
        the sigDocumentError is emitted. For the correct type the
        set value is compared to what it was meant to be set to.
        """

        self.connectionBox.connect(self.doc,
                                   SIGNAL('sigDocumentError'),
                                   self.connectionBox.slotSlot)
                                         
        # Loop over all the functions defined
        i = 0
        while i < len(self.signals):
            j = 0

            # Loop over all registered types to be passed to functions
            while j < len(self.types):

                # If the type doesn't match required type should return False
                # provide the correct error message and emit the 
                # sigDocumentError signal
                if self.types[j] != self.signals[i]['funcptype']:
                    test = self.signals[i]['function'](self.testparams[j])
                    self.assertEqual(test, False)
                    self.connectionBox.assertSignalArrived('sigDocumentError')

                # If it does match, should work and return correct param
                elif self.types[j] == self.signals[i]['funcptype']:
                    self.signals[i]['function'](self.testparams[j])
                    self.assertEqual(self.signals[i]['getmethod'](),
                                     self.signals[i]['returnexp'])

                j = j + 1

            # Need to initialise everything before next signal test
            self.doc.__init__()

            i = i + 1


                
class SignalsTestCase(AbstractTestCase):
    """Test the signals for the document
    """

    def tearDown(self):
        self.doc = None
        self.connectionBox = None

    def runSignalArrives(self, index):
        self.connectionBox.connect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']), 
                                   self.connectionBox.slotSlot)

        args = self.signals[index]['testparam']
        self.signals[index]['function'](*args)
        self.connectionBox.assertSignalArrived(self.signals[index]['signal'])
        self.connectionBox.disconnect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']), 
                                   self.connectionBox.slotSlot)

    def checkSignalArrives(self):
        """Check that the correct signals arrive as expected
        """

        index = 0
        while index < len(self.signals):
            self.runSignalArrives(index)
            index = index + 1

    def runSignalDoesNotArrive(self, index):
        """Check whether the sigDocModifiedXXX signal does not arrive"""

        self.connectionBox.connect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']+'XXX'),
                                   self.connectionBox.slotSlot)
        args = self.signals[index]['testparam']
        self.signals[index]['function'](*args)
        

        self.assertRaises(AssertionError,
                          self.connectionBox.assertSignalArrived,
                          signal = self.signals[index-1]['signal']+'XXX')

        # Disconnect ConnectionBox before running next test
        self.connectionBox.disconnect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']+'XXX'), 
                                   self.connectionBox.slotSlot)
        self.doc.__init__()


    def checkSignalDoesNotArrive(self):
        """Check whether the sigDocModifiedXXX signal does not arrive"""

        index = 0
        while index < len(self.signals):
            self.runSignalDoesNotArrive(index)
            index = index + 1

    def runArgumentToSignal(self, index):
        """Check whether the sigDocModified signal has the right
           number of arguments
        """
        self.connectionBox.connect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']),
                                   self.connectionBox.slotSlot)
        args = self.signals[index]['testparam']
        self.signals[index]['function'](*args)
        self.connectionBox.assertNumberOfArguments(
                                   self.signals[index]['returnspar'])

        # Disconnect ConnectionBox before running next test
        self.connectionBox.disconnect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']), 
                                   self.connectionBox.slotSlot)
        self.doc.__init__()

    def checkArgumentToSignal(self):
        """Check whether the sigDocModified signal has the right
           number of arguments
        """
        index = 0
        while index < len(self.signals):
            self.runArgumentToSignal(index)
            index = index + 1

    def runArgumentTypes(self, index):
        """Check whether the sigDocModified signal has the right 
           type of arguments.
        """
        self.connectionBox.connect(self.doc,                                   
                                   SIGNAL(self.signals[index]['signal']),
                                   self.connectionBox.slotSlot)
        args = self.signals[index]['testparam']
        self.signals[index]['function'](*args)
        self.connectionBox.assertArgumentTypes(
                                   self.signals[index]['returntype'])

        self.connectionBox.disconnect(self.doc, 
                                   SIGNAL(self.signals[index]['signal']), 
                                   self.connectionBox.slotSlot)
        self.doc.__init__()


    def checkArgumentTypes(self):
        """Check whether the sigDocModified signal has the right 
           type of arguments.
        """

        index = 0
        while index < len(self.signals):
            self.runArgumentTypes(index)
            index+=1

def suite():
    signalsTestSuite=unittest.makeSuite(SignalsTestCase, 'check')
    initTestSuite = unittest.makeSuite(InitTestCase, 'check')
    errorTestSuite = unittest.makeSuite(ErrorCatchingTestCase, 'check')
    testSuite = unittest.TestSuite([signalsTestSuite, 
                                    initTestSuite,
                                    errorTestSuite])
    return testSuite

def main():
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
    
        
if __name__ == '__main__':
    from TestingConnectionBox import *
    main()

        
        
        
        
