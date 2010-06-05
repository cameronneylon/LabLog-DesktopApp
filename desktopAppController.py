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
        self.initMenuBar()
        #self.initToolBar()
        self.initStatusBar()


    def initActions(self):
        #fileQuitIcon=QIconSet(QPixmap(filequit))
        self.actions = {}
        self.actions['fileQuit'] = QAction('Exit', self)

        self.connect(self.actions['fileQuit'],
                     SIGNAL('activated()'),
                     self.slotFileQuit)

        self.actions['multiPostDataUpload'] = QAction('Data upload', 
                                                      self)

        self.connect(self.actions['multiPostDataUpload'],
                     SIGNAL('activated()'),
                     self.slotMultiPostDataUpload)
        

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
        # Then add Blog Actions Menu to menu bar
        self.menuBar().addMenu(self.blogactionsmenu)

    def initStatusBar(self):
        self.statusBar().showMessage('Ready...')

    ################################################
    # UI and Document initialisation routines
    ###############################################

    def initBlogandUserMenu(self):

        # Initialise the menu
        self.blogandusermenu = QMenu()
        self.blogandusermenu.clear()
        self.blogandusermenu.setTitle('Blogs and usernames')
        self.menuBar().addMenu(self.blogandusermenu)

        # Collect the relevant items and create menus
        # First the blog server selection menu
        self.blogservermenu = QMenu()
        self.blogservermenu.setTitle('Select Blog Server')
        i=0
        for server in self.doc.blogserverlist:
            self.blogservermenu.addAction(server,
                      lambda i=i: self.slotBlogServerMenuActivated(i))
            i+=1

        # Then the current blog selection menu
        self.blogselectionmenu = QMenu()
        self.blogselectionmenu.setTitle('Select Blog')
        i=0
        for blog in self.doc.servertoblogmapping[self.doc.currentblogserver]:
            self.blogselectionmenu.addAction(blog,
                      lambda i=i: self.slotBlogSelectionMenuActivated(i))
            i+=1

        # Then the user name selection
        self.usernamemenu = QMenu()
        self.usernamemenu.setTitle('Select username')
        i=0
        for username in self.doc.usernamemapping[self.doc.currentblogserver]:
            self.usernamemenu.addAction(username, 
                      lambda i=i: self.slotUsernameMenuActivated(i))
            i+=1

        self.blogandusermenu.addMenu(self.blogservermenu)
        self.blogandusermenu.addMenu(self.blogselectionmenu)
        self.blogandusermenu.addMenu(self.usernamemenu)

    def initMultiPostDataUploadDoc(self):
        self.doc = desktopAppDoc.MultiPostDoc()
        self.connect(self.doc, SIGNAL('sigDocUpdateStatusBar'),
                                           self.updateStatusBar)


    def initMultiPostDataUploadView(self):
        self.view = desktopAppView.MultiPostView(self.doc)
        self.setCentralWidget(self.view)

        # Connect UI event signals to slot functions
        self.connect(self.view, SIGNAL('sigViewTitleModified'),
                                self.notifyDocTitleModified)
        self.connect(self.view, SIGNAL('sigViewPostTextModified'),
                                self.notifyDocPostTextModified)
        self.connect(self.view, SIGNAL('sigViewDataDirModified'),
                                self.notifyDocDataDirModified)
        self.connect(self.view, SIGNAL('sigViewDoUploadDir'),
                                self.notifyDocDoUploadDirectory)
        self.connect(self.view, SIGNAL('sigViewUseFilenameCheckedTRUE'),
                                self.notifyDocUseFilenameCheckedTrue)
        self.connect(self.view, SIGNAL('sigViewUseFilenameCheckedFALSE'),
                                self.notifyDocUseFilenameCheckedFalse)

        # Connect Document events to slot functions
        # Key event is sigDocCurrentBlogServerSet which requires
        # the Blog and User menus to be re-set

        self.connect(self.doc, SIGNAL('sigDocCurrentBlogServerSet'),
                               self.resetBlogandUserMenu)


###########################################
# Slot implementations
###########################################

    ####################
    # Slots from Primary Menu Actions
    ####################

    def slotFileQuit(self):
        pass

    def slotMultiPostDataUpload(self):
        self.initMultiPostDataUploadDoc()
        self.initMultiPostDataUploadView()
        self.initBlogandUserMenu()

    ####################
    # Slots from the Blog/Username Menu
    ####################

    def slotBlogServerMenuActivated(self, index):
        self.doc.setCurrentBlogServer(index)

    def slotBlogSelectionMenuActivated(self, index):
        self.doc.setCurrentBlog(index)

    def slotUsernameMenuActivated(self, index):
        self.doc.setCurrentUsername(index)

    ####################
    # Slots from the MultiPostDataUpload UI
    ####################

    def notifyDocTitleModified(self):
        """Notify the document when title line edit changed
        """
        logging.debug('Setting Post Title: ' + self.view.titleedit.text())
        self.doc.setPostTitle(self.view.titleedit.text())

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

    def notifyDocPostTextModified(self):
        """Notify the document when post content box changed
        """
        logging.debug('Setting Post Title: ' + self.view.posttext.toPlainText())
        self.doc.setPostContent(self.view.posttext.toPlainText())

    def notifyDocDataDirModified(self):
        """Notify the document when data directory box changed
        """
        logging.debug('Setting Post Title: ' + self.view.dirTextBox.text())
        self.doc.setDataDirectory(self.view.dirTextBox.text())

    def notifyDocDoUploadDirectory(self):
        """Notify the document when the upload button pressed
        """
        self.doc.doMultiPostDataUpload()

    ####################
    # Slots from the document that require menu or statusbar changes
    ####################

    def resetBlogandUserMenu(self):
        """Reset the blog and user selection menu for new server
        """

        # Reset the blog selection menu
        self.blogselectionmenu.clear()
        i=0
        for blog in self.doc.servertoblogmapping[self.doc.currentblogserver]:
            self.blogselectionmenu.addAction(blog,
                      lambda i=i: self.slotBlogSelectionMenuActivated(i))
            i+=1

        # Then the user name selection
        self.usernamemenu.clear()
        i=0
        for username in self.doc.usernamemapping[self.doc.currentblogserver]:
            self.usernamemenu.addAction(username, 
                      lambda i=i: self.slotUsernameMenuActivated(i))
            i+=1

    def updateStatusBar(self):
        """Update the status bar with the contents of self.doc.status
        """

        self.statusBar().showMessage(self.view.doc.status[-1])

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
        
        
