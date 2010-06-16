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
import logging
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import desktopAppDoc
import desktopAppView

class desktopApp(QMainWindow):
    def __init__(self, *args):
        apply(QMainWindow.__init__,(self, ) + args)
        self.setGeometry(100, 100, 600, 300)
        self.initActions()
        self.initPrefsDoc()
        self.initMenuBar()
        #self.initToolBar()
        self.initStatusBar()
        logging.debug('Initialising new app session')


    def initActions(self):
        """Function to initialise generic actions
        
        Actions that are initialised here include FileQuit which
        is not currently implemented. The multiple post Data
        upload action and the multple post creatiomn action.
        """

        #fileQuitIcon=QIconSet(QPixmap(filequit))
        self.actions = {}

        self.actions['fileQuit'] = QAction('Exit', self)
        self.connect(self.actions['fileQuit'],
                     SIGNAL('activated()'),
                     self.slotFileQuit)

        # Action for multi post Data Upload
        self.actions['multiPostDataUpload'] = QAction('Data upload', 
                                                      self)
        self.connect(self.actions['multiPostDataUpload'],
                     SIGNAL('activated()'),
                     self.slotMultiPostDataUpload)

        # Action for multiple post creation
        self.actions['multiPostCreation'] = QAction('Multiple posts',
                                                    self)
        self.connect(self.actions['multiPostCreation'],
                     SIGNAL('activated()'),
                     self.slotMultiPostCreation)


    
    def initPrefsDoc(self):
        """Function that initialises the preferences doc

        The preferences doc holds the lists of available servers as
        well as the relationship between servers, blogs, and 
        usernames. The method initialises the document for the prefs
        and then connects the Signal sigDocCurrentBlogServerSet to 
        the function that will we reset the menus with the appropriate
        blogs and usernames for that server.
        """

        # Create and initialise the Preferences Document
        self.prefs = desktopAppDoc.PrefsDoc()

        # Connect the signal to trigger the re-setting of the menus
        self.connect(self.prefs, SIGNAL('sigDocCurrentBlogServerSet'),
                               self.resetBlogandUserMenu)

    def initMenuBar(self):

        # Set up the File Menu
        self.filemenu = QMenu()
        self.filemenu.setTitle('&File')
        self.filemenu.addAction(self.actions['fileQuit'])
        self.menuBar().addMenu(self.filemenu)

        # Set up the Blog Actions Menu
        self.blogactionsmenu = QMenu()
        self.blogactionsmenu.setTitle('&Blog actions')
        self.blogactionsmenu.addAction(self.actions['multiPostDataUpload'])
        self.blogactionsmenu.addAction(self.actions['multiPostCreation'])
        # Then add Blog Actions Menu to menu bar
        self.menuBar().addMenu(self.blogactionsmenu)

        # Initialise the Blogs and Usernames menu
        self.blogandusermenu = QMenu()
        self.blogandusermenu.clear()
        self.blogandusermenu.setTitle('Blogs and usernames')
        self.menuBar().addMenu(self.blogandusermenu)

        # Collect the relevant items and create menus
        # First the blog server selection menu
        self.blogservermenu = QMenu()
        self.blogservermenu.setTitle('Select Blog Server')
        i=0
        for server in self.prefs.blogserverlist:
            self.blogservermenu.addAction(server,
                      lambda i=i: self.slotBlogServerMenuActivated(i))
            i+=1

        # Then the current blog selection menu
        self.blogselectionmenu = QMenu()
        self.blogselectionmenu.setTitle('Select Blog')
        i=0
        for blog in self.prefs.servertoblogmapping[
                                           self.prefs.currentblogserver]:
            self.blogselectionmenu.addAction(blog,
                      lambda i=i: self.slotBlogSelectionMenuActivated(i))
            i+=1

        # Then the user name selection
        self.usernamemenu = QMenu()
        self.usernamemenu.setTitle('Select username')
        i=0
        for username in self.prefs.usernamemapping[
                                      self.prefs.currentblogserver]:
            self.usernamemenu.addAction(username, 
                      lambda i=i: self.slotUsernameMenuActivated(i))
            i+=1

        self.blogandusermenu.addMenu(self.blogservermenu)
        self.blogandusermenu.addMenu(self.blogselectionmenu)
        self.blogandusermenu.addMenu(self.usernamemenu)

    def initStatusBar(self):
        self.statusBar().showMessage('Ready...')

    ################################################
    # UI and Document initialisation routines
    #
    # For each new form of interaction two initialisation methods are
    # required, one to initialise the appropriate document which will
    # be a subclass of AbstractPostDoc and placed in desktopAppDoc.py,
    # and one to initialise the connected view which will be a subclass
    # of AbstractPostView and placed in desktopAppView.py. The main
    # purpose of the initalisation is to connect up the appropriate
    # signals that are specific to that blog action. Generic connections
    # are provided by the generic init methods that should be called
    # by the specific methods.
    #
    ###############################################

    def initGeneralDocConnections(self):
        """The general function for connecting signals common to to all docs
        """
        self.connect(self.prefs, SIGNAL('sigDocUpdateStatusBar'),
                                           self.updateStatusBar)

    def initGeneralViewConnections(self):
        """The general function for connections signals common to all views

        The title text modified and post content modified signals are common
        to all documents and all views and are therefore handled by this 
        general method.
        """
        self.setCentralWidget(self.view)

        # Connect UI event signals to slot functions
        self.connect(self.view, SIGNAL('sigViewTitleModified'),
                                self.notifyDocTitleModified)
        self.connect(self.view, SIGNAL('sigViewSectionChanged'),
                                self.notifyDocSectionChanged)
        self.connect(self.view, SIGNAL('sigViewMetadataChanged'),
                                self.notifyDocMetadataChanged)
        self.connect(self.view, SIGNAL('sigViewPostTextModified'),
                                self.notifyDocPostTextModified)
        self.connect(self.view, SIGNAL('sigViewDoUpload'),
                                self.notifyDocDoUpload)

    def initMultiPostDataUploadDoc(self):
        """The initialisation method for MultiPostDataUpload Docs

        This also serves as the template for other initialisation methods. THe
        document must be created before the general init method is called as
        otherwise the document will not exist to connect the signals from.
        """

        self.doc = desktopAppDoc.MultiPostDataUploadDoc(self.prefs)
        self.initGeneralDocConnections()

    def initMultiPostDataUploadView(self):
        """The initialisation method for MultiPostDataUpload Views

        This also serves as a template for other view initialisation methods.
        The view must be created before the general init method is called and 
        also after the document is created as the document is a characteristic
        of the view.
        """

        # Create the view
        self.view = desktopAppView.MultiPostDataUploadView(self.doc)
        # Call the general connections method
        self.initGeneralViewConnections()

        # Connect all the signals that are specific to this view/doc pair
        self.connect(self.view, SIGNAL('sigViewDataDirModified'),
                                self.notifyDocDataDirModified)

        self.connect(self.view, SIGNAL('sigViewUseFilenameCheckedTRUE'),
                                self.notifyDocUseFilenameCheckedTrue)
        self.connect(self.view, SIGNAL('sigViewUseFilenameCheckedFALSE'),
                                self.notifyDocUseFilenameCheckedFalse)

    def initMultiPostCreationDoc(self):
        """Init method for multiple post creation document
        """

        self.doc = desktopAppDoc.MultiPostCreationDoc(self.prefs)
        self.initGeneralDocConnections()

    def initMultiPostCreationView(self):
        """Init method for the multiple post creation view
        """

        # Create the view and call general connections function
        self.view = desktopAppView.MultiPostCreationView(self.doc)
        self.initGeneralViewConnections()

        # Connect all the specific connections for this view/doc pair
        # The only new connection for this action is the spinbox
        self.connect(self.view, SIGNAL('sigViewNumpostsChanged'),
                                self.notifyDocNumpostsValueChanged)
        


###########################################
# Slot implementations
###########################################

    ####################
    # Slots from Primary Menu Actions
    ####################

    def slotFileQuit(self):
        pass

    ####################
    # Slots from Blog Actions Menu
    ####################


    def slotMultiPostDataUpload(self):
        """Initialisation method for the Multi Post Data Upload

        This function is called when the data upload is selected
        from the blog actions menu. It in turn calls the initialisation
        functions for the appropriate document and view subclasses.

        It is also useful as a template for other types of action.To 
        create a new type of action that the application can support on
        the blog it is necessary to create a method here that will call the
        intiatilisation methods when the appropriate menu item from the
        blog actions menu is selected.
        """
        logging.debug('Initialising MultiPost Data Upload')
        self.initMultiPostDataUploadDoc()
        self.initMultiPostDataUploadView()


    def slotMultiPostCreation(self):
        """The initialisaton method for multiple post creation
        """
        logging.debug('Initialising Multiple Post Creation')
        self.initMultiPostCreationDoc()
        self.initMultiPostCreationView()


    ####################
    # Slots from the Blog/Username Menu
    ####################

    def slotBlogServerMenuActivated(self, index):
        self.prefs.setCurrentBlogServer(index)

    def slotBlogSelectionMenuActivated(self, index):
        self.prefs.setCurrentBlog(index)

    def slotUsernameMenuActivated(self, index):
        self.prefs.setCurrentUsername(index)


    ####################
    # Slots shared between all the UIs
    ####################

    def notifyDocTitleModified(self):
        """Notify the document when title line edit changed
        """
        logging.debug('Setting Post Title: ' + self.view.titleedit.text())
        self.doc.setPostTitle(self.view.titleedit.text())

    def notifyDocSectionChanged(self):
        """Notify the document when post section changed
        """
        logging.debug('Setting Post Section: ' 
                             + self.view.metadatawidget.getSection())
        self.doc.setPostSection(self.view.metadatawidget.getSection())

    def notifyDocMetadataChanged(self):
        """Notify the document when metadata widget changes
        """
        logging.debug('Metadata Widget Changed: ' 
                      + str(self.view.metadatawidget.getMetadata()))
        self.doc.setPostMetadata(self.view.metadatawidget.getMetadata())

    def notifyDocPostTextModified(self):
        """Notify the document when post content box changed
        """
        logging.debug('Setting Post Content: ' 
                          + self.view.posttext.toPlainText())
        self.doc.setPostContent(self.view.posttext.toPlainText())

    def notifyDocDoUpload(self):
        """Notify the document when the upload button pressed
        """
        self.doc.doUpload()


    ####################
    # Slots from the MultiPostDataUpload UI
    ####################

    def notifyDocUseFilenameCheckedTrue(self):
        """Notify the document when usefilename checked
        """
        logging.debug('UseFilenameCheck: ' + 
                      str(self.view.usefilenamecheck.isChecked()))
        self.doc.setUseFilename(True)

    def notifyDocUseFilenameCheckedFalse(self):
        """Notify the document when usefilename unchecked
        """
        logging.debug('UseFilenameCheck: ' + 
                      str(self.view.usefilenamecheck.isChecked()))
        self.doc.setUseFilename(False)     

    def notifyDocDataDirModified(self):
        """Notify the document when data directory box changed
        """
        logging.debug('Setting Post Title: ' + self.view.dirTextBox.text())
        self.doc.setDataDirectory(self.view.dirTextBox.text())


    ####################
    # Slots from the MultiPostDataUpload UI
    ####################

    def notifyDocNumpostsValueChanged(self):
        """Notify the document when the numposts spingbox value changes
        """
        logging.debug('Numposts Spinbox set to: ' +
                        str(self.view.numpostspinbox.value()))
        self.doc.setNumPosts(self.view.numpostspinbox.value())

    ####################
    # Slots from the document that require menu or statusbar changes
    ####################

    def resetBlogandUserMenu(self):
        """Reset the blog and user selection menu for new server
        """

        # Reset the blog selection menu
        self.blogselectionmenu.clear()
        i=0
        for blog in self.prefs.servertoblogmapping[
                                            self.prefs.currentblogserver]:
            self.blogselectionmenu.addAction(blog,
                      lambda i=i: self.slotBlogSelectionMenuActivated(i))
            i+=1

        # Then the user name selection
        self.usernamemenu.clear()
        i=0
        for username in self.prefs.usernamemapping[
                                       self.prefs.currentblogserver]:
            self.usernamemenu.addAction(username, 
                      lambda i=i: self.slotUsernameMenuActivated(i))
            i+=1

    def updateStatusBar(self):
        """Update the status bar with the contents of self.doc.status
        """

        self.statusBar().showMessage(self.prefs.status[-1])


def main(args):
    LOG_FILENAME = '/logging.out'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

    app=QApplication(args)
    docview = desktopApp()
    #app.setMainWidget(docview)
    docview.show()
    app.exec_()
    
if __name__=="__main__":
    main(sys.argv)        
        
        
