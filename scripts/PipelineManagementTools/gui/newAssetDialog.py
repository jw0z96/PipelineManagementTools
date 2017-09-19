#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

class NewAssetDialog(QDialog):
	def __init__(self, parentWindow = None, *args, **kwargs):
		super(NewAssetDialog, self).__init__(parentWindow, *args, **kwargs)
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/newAssetDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		self.setModal(True)

		self.ui.dialogButtonBox.rejected.connect(self.close)
		self.ui.dialogButtonBox.accepted.connect(self.createNewAsset)
		self.ui.filePathPushButton.clicked.connect(self.filePathDialog)

	def createNewAsset(self):
		print "checking asset name & path"

	def filePathDialog(self):
		assetDir = os.environ['MAYA_ASSET_DIR']
		diag = QFileDialog(self)
		diag.setModal(True)
		newFilePath = diag.getOpenFileName(self,
			"Select master file",
			assetDir,
			"Maya scene files (*.ma *.mb)")[0]
		print "full file path: "+newFilePath

		# if the file path is valid
		if newFilePath.startswith(assetDir):
			fp = newFilePath.replace(assetDir, '')
			self.ui.filePathLineEdit.clear()
			self.ui.filePathLineEdit.insert(fp)
		# if the file path wasn't null (user closed browser)
		elif newFilePath:
			QMessageBox.critical(self, "Error", "Selected file is not within $MAYA_ASSETS_DIR:\n"+assetDir)

