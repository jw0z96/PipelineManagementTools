#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

class GatherDialog(QDialog):
	def __init__(self, asset, parentWindow = None, *args, **kwargs):
		super(GatherDialog, self).__init__(parentWindow, *args, **kwargs)
		self.selectedAsset = asset
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/gatherDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# set regex for namespace
		nameSpaceRegex = QRegExp("[A-Za-z0-9_]+")
		nameSpaceValidator = QRegExpValidator(nameSpaceRegex, self.ui.nameSpaceLineEdit)
		self.ui.nameSpaceLineEdit.setValidator(nameSpaceValidator)

		# set callbacks & ui text
		self.ui.assetLabel.setText("Gathering " + self.selectedAsset)
		self.ui.buttonBox.rejected.connect(self.close)
		self.ui.buttonBox.accepted.connect(self.accept)
