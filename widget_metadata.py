from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging
import sys

class MenuPair(QWidget):
    """Pair of coupled menus for selecting key value pairs
    """

    def __init__(self, keymenuitems = [], keytovaluesmapping = {}, *args):
        apply(QWidget.__init__, (self,) + args)

        logging.debug('widget_metadata.py: Initialising MenuPair')
        self.key = None
        self.value = None
        self.keymenuitems = keymenuitems
        self.keytovaluesmapping = keytovaluesmapping

        self.hbox = QHBoxLayout()

        # Set up the key menu
        self.keymenu = QComboBox()
        self.keymenu.setEditable(True)
        self.initKeyMenu()
        self.connect(self.keymenu, 
                          SIGNAL('currentIndexChanged(QString)'),
                          self.keyMenuItemSelected)

        # Set up the value menu
        self.valuemenu = QComboBox()
        self.valuemenu.setEditable(True)
        self.initValuesMenu()
        self.connect(self.keymenu,
                          SIGNAL('currentIndexChanged(text)'),
                          self.valueMenuItemSelected)

        # Organise the layout
        self.hbox.addWidget(self.keymenu)
        self.hbox.addWidget(self.valuemenu)
        self.setLayout(self.hbox)

    def keyMenuItemSelected(self, menuitem):
        """Method to capture a new key menu selection 

        Method calles when menu item is selected manually or
        programmatically. Need to capture the item Text and
        set self.key and then reinitialise the value menu.
        """
        logging.debug("Key Menu Item triggered: " + menuitem)
        self.key = menuitem
        self.initValuesMenu()

    def valueMenuItemSelected(self):
        """Method to capture a new value menu selection
        """
        self.value = self.valuemenu.itemText()
        

    def initKeyMenu(self):
        """Initialise values in the Key menu
        """
        self.keymenu.clear()
        for key in self.keymenuitems:
            self.keymenu.addItem(key)
        if len(self.keymenuitems) > 0:
            self.key = self.keymenuitems[0]

    def initValuesMenu(self):
        """Initialise values in the Value Menu

        The values are stored in a dictionary of lists of the form
        {'key1':['value1', 'value2'...], 'key2' ...}
        There are situations (e.g. for a new key) where the key may
        not be in the dictionar. In these cases we want to create a
        blank combobox ready for text entry. If values are available
        the menu is populated with these.
        """
        
        logging.debug("Initialising Value Menu with key: " + str(self.key))
        # Clear the values menu
        self.valuemenu.clear()
        # If the key is in the mapping dictionary with associated values
        # then populate the menu with those values
        if str(self.key) in self.keytovaluesmapping:
            print self.keytovaluesmapping[str(self.key)]

            for value in self.keytovaluesmapping[str(self.key)]:
                self.valuemenu.addItem(value)

        # Otherwise just leave the menu blank
        else:
            logging.debug("Self.key not in mapping dict")

    def getKey(self):
        return self.key

    def getValue(self):
        return self.value

    def setKeyMenuEnabled(self, boolean):
        # TODO check it is a boolean incoming
        if boolean:
            self.keymenu.setEnabled(True)
        elif boolean == False:
            self.keymenu.setEnabled(False)
        else:
            pass

        return self.keymenu.isEnabled()

    def setValueMenuEnabled(self, boolean):
        # TODO check boolean incomig
        
        if boolean:
            self.valuemenu.setEnabled(True)
        elif boolean == False:
            self.valuemenu.setEnabled(False)
        else:
            pass

        return self.valuemenu.isEnabled()
            
            
        


class MetadataWidget(QWidget):
    """Blog post metadata widget

    The object is to have a widget that starts with one double menu pair
    to select the section and plus and minus buttons to add extra menu
    pairs for the addition of extra key value pairs.
    """

    def __init__(self, keymenuitems =[], keytovaluesmapping = {}, *args):
        apply(QWidget.__init__, (self,) + args)

        # self.metadata = {'section' : ''}
        self.keymenuitems = keymenuitems
        self.keytovaluesmapping = keytovaluesmapping

        # Set up a list to hold refs to menu pair instances
        self.menupairlist = []

        # Set up the widget with appropriate geometry and spacing
        self.grid = QGridLayout()
        self.label = QLabel('Metadata')

        # Set up the section menu
        self.section = MenuPair(keymenuitems = ['Section'],
                                keytovaluesmapping = self.keytovaluesmapping)
        self.section.keymenu.setEnabled(False)
        

        # Set up the plus button
        self.plusbutton = QToolButton()
        self.plusbutton.setIcon(QIcon('images/onebit_31.png'))
        self.connect(self.plusbutton,
                          SIGNAL('clicked()'),
                          self.addMenuPair)

        # And the minus button (deactivated on init)
        self.minusbutton = QToolButton()
        self.minusbutton.setIcon(QIcon('images/onebit_33.png'))
        self.minusbutton.setEnabled(False)
        self.connect(self.minusbutton,
                          SIGNAL('clicked()'),
                          self.removeMenuPair)

        # Initial layout
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.section, 1, 0)
        self.grid.addWidget(self.plusbutton, 1, 1)
        self.grid.addWidget(self.minusbutton, 1, 2)

        self.setLayout(self.grid)

    def addMenuPair(self):
        """Add a menupair for selecting a new key and value
        """

        # Create the new menupair
        newmenupair = MenuPair(keymenuitems = self.keymenuitems,
                               keytovaluesmapping = self.keytovaluesmapping)
        # Add menupair reference to list
        self.menupairlist.append(newmenupair)
        # Setup the position of the new menupair at bottom of current ones
        self.grid.addWidget(self.menupairlist[-1], 
                               (len(self.menupairlist)+1), 0)
        # Replace the buttons next to lowest menupair
        self.repositionPlusMinusButtons()
        self.setLayout(self.grid)
        self.minusbutton.setEnabled(True)

    def removeMenuPair(self):
        """Remove a menupair when not needed any more
        """
        self.grid.removeWidget(self.menupairlist[-1])
        self.menupairlist.pop().destroy()

        for menupair in self.menupairlist:
            self.grid.removeWidget(menupair)

        i=1
        for menupair in self.menupairlist:
            i+=1
            self.grid.addWidget(menupair, i, 0)

        self.repositionPlusMinusButtons()
        self.setLayout(self.grid)
        print len(self.menupairlist)
        if len(self.menupairlist) == 0:
            self.minusbutton.setEnabled(False)

    def repositionPlusMinusButtons(self):
        """Reposition the add and remove menu buttons
        """
        self.grid.removeWidget(self.plusbutton)
        self.grid.removeWidget(self.minusbutton)
        self.grid.addWidget(self.plusbutton, (len(self.menupairlist)+1), 1)
        self.grid.addWidget(self.minusbutton, (len(self.menupairlist)+1), 2)

    def getMetadata(self):
        """Method to return metadata as dictionary

        Method creates a dictionary by iterating over the menupairs
        and obtaining the key and value for each one. Any cases where
        the getKey() and getValue() methods return None are then popped
        from the dictionary.
        """

        self.metadata = {}
        self.metadata['Section'] = self.section.getValue()
        for menupair in self.menupairlist:
            if menupair.getKey() and menupair.getValue():
                self.metadata[menupair.getKey()] = menupair.getValue()

        return self.metadata


def main(args):
    LOG_FILENAME = '/logging.out'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    testkeys = ['1', '2', '3']
    testvaluesmapping = {'1': ['one', 'won'],
                         '2': ['too', 'to', 'two'],
                         'Section': ['data', 'notes']}
    app=QApplication(args)
    docview = MetadataWidget(keymenuitems = testkeys,
                             keytovaluesmapping = testvaluesmapping)
    #app.setMainWidget(docview)
    docview.show()
    app.exec_()
    
if __name__=="__main__":
    main(sys.argv)      

        
        
