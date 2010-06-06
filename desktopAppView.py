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
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class AbstractPostView(QWidget):
    """Abstract base class for UI widgets for each type of action.

    The abstract class provides only the post title, text content
    and the upload buttons. Layout should be handled in specific
    subclasses as this will depend on the number of subwidgets and
    their relative importance. Overall geometry is set in the 
    abstract class currently to match the main window.

    Window title and labels for Post Title widget are set but should
    be overwritten in subclasses. Metadata is currently not implemented
    but should be setup in the abstract class because it is a general
    requirement. The grid layout is created but not used.
    """

    def __init__(self, doc, *args):
        apply(QWidget.__init__, (self,) + args)
        
        # Set the passed document as the document of the view
        # The document is created by the controller just before
        # the view so it should be the right type. Probably a good
        # idea to provide a check of this in each subclass.
        self.doc = doc

        # Set up the window, title, grab focus and set layout as grid
        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle('Directory LaBLog Upload')
        self.setFocus()
        self.grid = QGridLayout()

        # Text box for post names
        self.posttitle = QLabel('Post title')
        self.titleedit = QLineEdit()

        # Text box for post text content. Only accepts plain text
        # TODO metadata setting
        self.posttexttitle = QLabel('Post text')
        self.posttext = QTextEdit()
        self.posttext.setAcceptRichText(False)

        # The upload to blog button
        self.uploadButton = QPushButton('Upload!', self)

        ####################
        #
        # Connections to shared actions to be notified to the document
        #
        # These actions need to signal the Controller so as to trigger
        # other actions. Shared actions implemented in the abstract 
        # class include the Upload action, changes to post title and to
        # post content.
        # 
        ####################

        # Action on modifying the Post Title line edit box
        self.connect(self.titleedit, SIGNAL('editingFinished()'),
                                     self.emitViewTitleModified)

        # Action on modifying the Post Content text edit
        self.connect(self.posttext, SIGNAL('textChanged()'),
                                    self.emitViewPostTextModified)

        # Action on pressing Upload button
        # TODO generalise the doUpload signal
        self.connect(self.uploadButton, SIGNAL('clicked()'),
                                        self.emitViewDoUpload)

        ####################
        #
        # Connections to signals originating in the App Document
        #
        # Signals to be received from the document are those triggered
        # on a change in the post title, the post content being 
        # changed and the data directory being set. This is also
        # where error messages from the Document get caught.
        #
        ####################

        # Change of post title in document
        self.connect(self.doc, SIGNAL('sigDocPostTitleSet'),
                               self.setPostTitleLineEdit)

        # Change of post content in document
        self.connect(self.doc, SIGNAL('sigDocPostContentChanged'),
                               self.setPostContentTextEdit)
        # Document error raised
        self.connect(self.doc, SIGNAL('sigDocumentError'),
                               self.notifyUserDocumentError)

        # Post upload in progress, so block the GUI
        self.connect(self.doc, SIGNAL('sigDocUploading'),
                               self.blockallinputs)

        # Multipost data upload complete
        # TODO generalise the upload complete signal
        self.connect(self.doc, SIGNAL('sigDocFinishedUploading'),
                               self.notifyUserDataUploadComplete)


    ####################
    #
    # Methods for handling incoming signals from the Document
    #
    # Shared methods are those for when the values of the post title or
    # post content is changed in the document, when a document error
    # is raised and when an upload is in progress, requiring that all
    # the inputs be blocked.
    #
    ####################

    def setPostTitleLineEdit(self, signal):
        """Method triggered when doc signals Post Title Changed

        First check whether is the same as current text so as to
        prevent race condition. If it is different (e.g. if set
        via script or macro, then change linedit to match. This
        method is connected to sigDocPostTitleSet
        """

        # If incoming string is the same then ignore
        if self.doc.posttitle == self.titleedit.text():
            return
        # If the text edit is disabled then ignore
        elif self.titleedit.isEnabled() == False:
            return
        else:
            self.titleedit.setText(self.doc.posttitle)

    def setPostContentTextEdit(self, signal):
        """Method triggered when doc signals Post Content Changed

        First check whether is the same as current text so as to
        prevent race condition. If it is different (e.g. if set
        via script or macro, then change linedit to match. This
        method is connected to sigDocPostContentChanged
        """

        if self.doc.postcontent == self.posttext.toPlainText():
            return
        else:
            self.posttext.clear()
            self.posttext.insertPlainText(self.postcontent)
 
    def notifyUserDocumentError(self, e):
        """Method triggered by Document error catching routines
        
        The signal sigDocumentError fires when incorrect parameters
        are passed to the Document. Under most circumstances this
        shouldn't bother the user but it is useful for notification
        purposes.
        """

        message = "Document Error\n\n" + str(e)
        errormessage = QMessageBox.warning(self,
                            'QtMessageBox.warning()', message)

    def blockallinputs(self):
        """Method called when all inputs need to be deactivated

        Currently called only when a data upload is in progress.
        """

        self.setDisabled(True)

    ####################
    #
    # Methods for notifying actions to the App Controller
    #
    # Actions from the GUI that need to notify the document of 
    # changes. Shared methods in the abstract class include the 
    # signals triggered by modifying the post title line edit or the 
    # post content, and the Upload button being pressed.
    #
    ####################

    def emitViewTitleModified(self):
        """Notify the document when title line edit changed
        """
        self.emit(SIGNAL('sigViewTitleModified'))

    def emitViewPostTextModified(self):
        """Notify the document when post content box changed
        """
        self.emit(SIGNAL('sigViewPostTextModified'))


    # TODO generalise this for all Upload actions
    def emitViewDoUpload(self):
        """Notify the document when the upload button pressed
        """
        self.emit(SIGNAL('sigViewDoUpload'))

class MultiPostDataUploadView(AbstractPostView):
    def __init__(self, doc, *args):
        apply(AbstractPostView.__init__, (self, doc) + args)


        # Create checkbox for 'use filenames' option
        self.usefilenamecheck = QCheckBox('Use filenames?', self)

        # Button to open file dialogue and text edit to display path
        self.selectDirButton = QPushButton('Select directory', self)
        self.dirTextBox = QLineEdit()

        # Setting up the layout of the widget
        self.grid.addWidget(self.posttitle, 0, 0)
        self.grid.addWidget(self.titleedit, 0, 1)
        self.grid.addWidget(self.usefilenamecheck, 0, 2)
        self.grid.addWidget(self.posttexttitle, 1, 0)
        self.grid.addWidget(self.posttext, 1, 1, 1, 2)
        self.grid.addWidget(QLabel(''), 3, 0)
        self.grid.addWidget(self.selectDirButton, 4, 0)
        self.grid.addWidget(self.dirTextBox, 4, 1, 1, 2)
        self.grid.addWidget(self.uploadButton, 5, 2)

        self.setLayout(self.grid)

        ####################
        # Connections to local actions in the GUI window
        #
        # These actions are entirely internal to the GUI so
        # do not need to be notified elsewhere. The directory
        # dialog emits a signal when it returns to be caught
        # and sent onto the application document.
        #
        ####################

        # Action on pressing directory selection button
        self.connect(self.selectDirButton, 
                         SIGNAL('clicked()'),
                         self.selectDirectoryDialog)


        ####################
        #
        # Connections to actions to be notified to the document
        #
        # These actions need to signal the Controller so as to trigger
        # other actions. This includes the actual upload process,
        # changes in the post title, post content, and data 
        # directory text edit boxes. The document data directory is 
        # also set within the dialog box routine. 
        # 
        ####################

        # Use filename checkbox state changed
        self.connect(self.usefilenamecheck, SIGNAL('stateChanged(int)'),
                         self.emitFilenameCheckClicked)

        # Action on modifying the Data Directory text edit
        self.connect(self.dirTextBox, SIGNAL('editingFinished()'),
                                      self.emitViewDataDirModified)


        ####################
        #
        # Connections to signals originating in the App Document
        #
        # Signals specific to the MultiPostDataUpload View are the
        # signal emitted when the usefilename flag is changed and
        # when the data directory is changed. 
        #
        ####################

        # Usefilename state toggled in document
        self.connect(self.doc, SIGNAL('sigDocUseFilenameChanged'),
                               self.enableordisablePostTitleLineEdit)


        # Change of data directory
        self.connect(self.doc, SIGNAL('sigDocDataDirectoryChanged'),
                               self.setDataDirectoryLineEdit)


    ####################
    #
    # Methods for handling incoming signals from the Document
    #
    # Specific methods required for the MultiPostDataUpload view
    # are to deactivate the PostTitle line edit if the use filename
    # option is activated, to set the data directory line edit when the
    # data directory changes in the document. A method is also provided
    # to trigger a dialog box to select the directory. There is also a 
    # specific upload finished notification implemented to show how many
    # of the data objects and posts were successful.
    #
    ####################


    def enableordisablePostTitleLineEdit(self, signal):
        """Toggle the state of post title box

        Method checks the state of the checkbox and then either deactivates
        or activates the line edit box as appropriate.
        """

        # If checkbox is ticked then check whether text box is enabled
        # and if so then disabled and set blank TODO store value for 
        # later recovery

        if self.doc.getUseFilename() == True:
            if self.titleedit.isEnabled() == True:
                self.titleedit.setDisabled(True)
                self.titleedit.setText('')

        # If checkbox unticked then enable the line edit text box and
        # set the focus to the input box.
        elif self.doc.getUseFilename() == False:
            if self.titleedit.isEnabled() == False:
                self.titleedit.setEnabled(True)
                self.titleedit.setText(self.doc.getPostTitle())
                self.titleedit.setFocus()

    
    def selectDirectoryDialog(self):
        """Triggers file dialog to select directory for upload"""

        directory = QFileDialog.getExistingDirectory(self, 
                    'Open Directory',
                    '/home')
        self.dirTextBox.setText(directory)
        self.doc.setDataDirectory(directory)

    def setDataDirectoryLineEdit(self, signal):
        """Method triggered when doc signals Post Title Changed

        First check whether is the same as current text so as to
        prevent race condition. If it is different (e.g. if set
        via script or macro, then change linedit to match. This
        method is connected to sigDocDataDirectoryChanged.
        """

        if self.doc.datadirectory == self.dirTextBox.text():
            return
        else:
            self.dirTextBox.setText(self.doc.datadirectory) 


    def notifyUserDataUploadComplete(self):
        """Dialog box triggered when data upload is complete
        """
        
        message = ("Upload succeeded\n\n For " + str(self.doc.length) + 
                   " data objects, " + str(self.doc.data_fail) + 
                   " data uploads failed and " + str(self.doc.post_fail) +
                   " post creations failed") 
        notify = QMessageBox.warning(self,
                             'QtMessageBox.warning()', message)

    ####################
    #
    # Methods for notifying actions to the App Controller
    #
    # Specific actions from the GUI for the MultiPostDataUpload View 
    # that need to notify the document of include the signals triggered 
    # by the data directory being changed and the usefilename checkbox
    # being selected.
    #
    ####################

    def emitViewDataDirModified(self):
        """Notify the document when data directory box changed
        """
        self.emit(SIGNAL('sigViewDataDirModified'))


    def emitFilenameCheckClicked(self):
        """Action called when Use File Name checkbox is clicked"""

        if self.usefilenamecheck.isChecked() == True:
            self.emit(SIGNAL('sigViewUseFilenameCheckedTRUE'))

        elif self.usefilenamecheck.isChecked() == False:
            self.emit(SIGNAL('sigViewUseFilenameCheckedFALSE'))
        
        else:
            pass









