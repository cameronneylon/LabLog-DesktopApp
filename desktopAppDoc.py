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
# waiver at http://github.com/cameronneylon/LaBLog-Utilities. The 
# application requires a range of modules from the Python 2.6 standard 
# library.  

import sys
import os.path
import unittest
import logging
import lablogpost
from PyQt4.QtCore import *

class PrefsDoc(QObject):
    """Class for containing preferences and blog information

    This class handles the record of the currently selected
    blog server, blog, and username. The document is created
    when the application runs and persists for the the running
    of the session. At the moment it doesn't persist between
    sessions.
    """

    def __init__(self, *args):
        QObject.__init__(self, *args)

        self.initBlogServerList()
        self.initCurrentBlogServer()
        self.initServertoBlogMapping()
        self.initCurrentUsername()
        self.initCurrentBlog()
        self.status=[]

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

####################################################################
#                                                                  #
# Post Document Objects                                            #
#                                                                  #
# Documents that describe post objects are placed here. The        # 
# AbstractPostDoc is the base class that should be subtyped to     #
# create new types of document to support new classes of action.   #
# In particular the doUpload method will need to be overwritten    #
# in each case to handle the details of the particular upload      #
# methods.                                                         #
#                                                                  #
####################################################################

class AbstractPostDoc(QObject):
    """Abstract base class with common methods for Post Documents

    The Abstract class currently holds notions of the blog server
    blogs, usernames, and current blogs as well as elements for
    the post objects of PostTitle and PostContent. Both are 
    assumed to be QStrings. Specific document classes will treat
    these strings in different ways. If a non-QString Title or
    Content are required these methods should be overwritten.

    The doUpload method is provided here as a place holder and should
    be overwritten for each specific document class. It is here simply
    to provide the template for the more specific upload methods.
    """

    def __init__(self, prefs, *args):
        QObject.__init__(self, *args)

        self.initPostTitle()
        self.initPostContent()
        self.initPostMetadata()
        self.prefs = prefs

        self.status = []

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

    def initPostSection(self):
        self.postsecton = ''

    def setPostSection(self, string):
        logging.debug('desktopAppDoc: Set Post Section: Received: ' 
                                                   + str(string))
        try: 
            assert type(string) == str, 'Section must be a string'
            self.postsection = str(string)
            self.emit(SIGNAL('sigDocPostSectionSet'), (self.postsection,))
            return True
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getPostSection(self):
        return self.postsection
    
    def initPostMetadata(self):
        self.postmetadata = {}

    def setPostMetadata(self, dictionary):
        logging.debug('desktopAppDoc: Set Post Metadata: Received: ' 
                                                + str(dictionary))
        try: 
            assert type(dictionary) == dict, 'Metadata must be a dictionary'
            self.postmetadata = dictionary
            self.emit(SIGNAL('sigDocPostMetadataSet'), (self.postmetadata,))
            return True
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getPostMetadata(self):
        return self.postmetadata

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

    def doUpload(self):
        """A template method for creating the Upload Method for subclasses

        This function should be overwritten for any subclass. The application
        expects the signals described here to notify that an upload is in
        progress and there the GUI should be disabled and that the upload
        is complete and the user can now proceed after the appropriate 
        dialog is created.
        """

        # Check that required information is available
        try:
            assert ((self.posttitle != '') or 
                    (self.usefilename == True)), 'Need post title'
            assert self.postcontent != '', 'Need post text'
        
        # If insufficient information is available raise a warning dialog
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

        self.status.append('Sending data posts to server')
        self.emit(SIGNAL('sigDocUpdateStatusBar'))
        self.emit(SIGNAL('sigDocUploading'))

        # DO THE UPLOAD OF POSTS AND DATA HERE

        self.emit(SIGNAL('sigDocFinishedUploading'))

        self.status.append() # INSERT AN APPROPRIATE STATUS MESSAGE


class MultiPostDataUploadDoc(AbstractPostDoc):
    """Document for a multi-post directory data upload

    Document model class that describes the information for the 
    posting of a directory of data files as a set of blog posts.
    A subclass of the Abstract Post Document class that provides
    additional methods to select a directory of files to 
    upload, a method to set a flag that will use the filename
    of each data file as the title of the blog post and the
    final upload method. 

    If the filenames are not used as post title the given post
    title simply has a number incremented at the end. Currently
    the post content is not modified.
    """

    def __init__(self, prefs, *args):
        AbstractPostDoc.__init__(self, prefs, *args)

        self.initUseFilename()
        self.initDataDirectory()


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


    def doUpload(self):
        """Overwritten method for doing the multiple post upload"""

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
        self.emit(SIGNAL('sigDocUploading'))
       
        self.filelist = []
        for file in os.listdir(self.datadirectory):
            self.filelist.append(os.path.join(self.datadirectory, file))


        posts = lablogpost.MultiDataFileUpload(
                **{'filelist'   : self.filelist,
                   'postnames'  : str(self.posttitle),
                   'posttext'   : str(self.postcontent),
                   'metadata'   : self.getPostMetadata,
                   'server_url' : str(self.prefs.currentblogserver),
                   'blog_sname' : str(self.prefs.currentblog),
                   'username'   : str(self.prefs.currentusername),
                   'section'    : self.getPostSection(),
                   'uid'        : lablogpost.DEFAULT_UID
                   })

        # Record the set of successes and fails and send signals
        self.data_fail, self.post_fail, self.length = posts.doUpload()
        self.status.append('Uploaded ' + str(self.length) + ' data objects')
        self.emit(SIGNAL('sigDocFinishedUploading'))


class MultiPostCreationDoc(AbstractPostDoc):
    """A class to support the creation of sets of incremented posts

    The MultiPostCreation method is intended to support the creation of
    multiple posts that increment in a predictable way. Usually these
    will be a set of physical samples, fractions, or reactions that
    are to be represented by a set of essentially identical posts.

    The document requires only a title, some text, a required number
    of posts and an overwritten upload method that will incrememnt 
    through the number of desired posts. Currently the system adds a 
    number to the end of the post title which increments for each
    post.
    """

    def __init__(self, prefs, *args):
        AbstractPostDoc.__init__(self, prefs,*args)

        # Internal variable for setting number of posts required
        self.numposts = 0

    def setNumPosts(self, integer):
        """Function to set the number of posts required
        """

        try:
            assert type(integer) == int, 'Number of posts must be integer'
            self.numposts = integer
            self.emit(SIGNAL('sigDocNumPostsChanged'), (self.numposts,))
            return True

        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

    def getNumPosts(self):
        return self.numposts

    def doUpload(self):
        """Specific upload method for multiple post creation
        """

        logging.debug('Starting mutlple post creation upload')
        # Check that required information is available
        try:
            assert self.posttitle != '', 'Need post title'
            assert self.postcontent != '', 'Need post text'
            assert self.numposts > 0, 'Doing less than one post?'

        
        # If insufficient information is available raise a warning dialog
        except AssertionError, e:
            self.emit(SIGNAL('sigDocumentError'), (e, ))
            return False

        # Prepare a dictionary to call the LabLogPost init method
        # TODO handle metadata
        inputdictionary = {'username'   : self.prefs.getCurrentUsername(),
                           'content'    : str(self.getPostContent()),
                           'section'    : self.getPostSection(),
                           'blog_sname' : self.prefs.getCurrentBlog(),
                           'metadata'   : self.getPostMetadata()}

        # Send signals that upload is about to start
        self.status.append('Sending posts to server')
        self.emit(SIGNAL('sigDocUpdateStatusBar'))
        self.emit(SIGNAL('sigDocUploading'))

        # Set up some counters for the upload process
        i=0
        self.post_fail = 0
        self.post_failures = []
        self.post_success = 0
        
        # Do the uploads
        while i < self.numposts:
            i+=1
            #Setup the post title
            inputdictionary['title'] = str(self.getPostTitle()) + '-' + str(i)
            #Create the post and upload it
            post = lablogpost.LaBLogPost(**inputdictionary)
            post.doPost(url = self.prefs.getCurrentBlogServer(),
                        uid = lablogpost.DEFAULT_UID)

            if post.posted:
                self.post_success += 1
                self.emit(SIGNAL('sigDocPostUploadSuccess'))

            elif post.posted == False:
                self.post_fail += 1
                self.post_failures.append(i)

            else:
                # raise ValueError('post.posted should be type bool')
                pass

        #TODO retry the posting for those that have failed?

        # Signal that upload is complete and update status
        self.status.append('Uploaded ' + str(i) + 'posts with ' +
                           str(self.post_fail) + ' failures.')
        self.emit(SIGNAL('sigDocFinishedUploading'))            
       

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

        
        
        
        
