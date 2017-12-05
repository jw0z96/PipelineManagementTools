#!/usr/bin/python
import os.path

try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	from PySide2.QtUiTools import *
except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide.QtWidgets import *
	from PySide.QtUiTools import *

class GatherDialog(QDialog):
	def __init__(self, asset, masterPath, parentWindow = None, *args, **kwargs):
		super(GatherDialog, self).__init__(parentWindow, *args, **kwargs)
		self.selectedAsset = asset
		self.masterPath = masterPath
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/gatherDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# set namespace autofill
		autofill = os.path.splitext(os.path.basename(self.selectedAsset))[0]
		self.ui.nameSpaceLineEdit.setText(autofill)

		# set regex for namespace
		nameSpaceRegex = QRegExp("[A-Za-z0-9_]+")
		nameSpaceValidator = QRegExpValidator(nameSpaceRegex, self.ui.nameSpaceLineEdit)
		self.ui.nameSpaceLineEdit.setValidator(nameSpaceValidator)

		# set callbacks & ui text
		self.ui.assetLabel.setText("Gathering " + self.masterPath)
		self.ui.buttonBox.rejected.connect(self.close)
		self.ui.buttonBox.accepted.connect(self.accept)
