# py2exe setup script
# This needs to be run as "python setup.py py2exe" from a directory above the code directories
# The images directory will then need to be added manually to the distribution 

from distutils.core import setup
import py2exe
setup(windows=["code/LaBlog-DesktopApp/desktopAppController.py"], options={"py2exe": {
         "includes": ["sip", "PyQt4.QtGui", "desktopAppDoc", "desktopAppView", "widget_metadata"]}})