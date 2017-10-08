#!/usr/bin/python
import os.path

try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2 import __version__
except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide import __version__

from gui import assetManagerUI
reload(assetManagerUI)

import qdarkstyle

# Get entrypoint through which we control underlying Qt framework
app = QApplication([])

window = assetManagerUI.AssetManagerUI()
window.setStyleSheet(qdarkstyle.load_stylesheet())
window.show()

app.exec_()
