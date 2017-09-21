#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from PipelineManagementTools import assetUtils
reload(assetUtils)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class UpdateAssetDialog(QDialog):
	def __init__(self, asset, parentWindow = None, *args, **kwargs):
		super(UpdateAssetDialog, self).__init__(parentWindow, *args, **kwargs)
		self.asset = asset
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/updateAssetDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()
		# set callbacks & ui text
		self.ui.dialogButtonBox.rejected.connect(self.close)
		self.ui.dialogButtonBox.accepted.connect(self.updateAsset)
		self.ui.filePathPushButton.clicked.connect(self.filePathDialog)
		self.ui.assetNameLabel.setText("Updating asset: " + self.asset)
		# set regex for comment
		commentRegex = QRegExp("[A-Za-z0-9 _.,?!]+")
		commentValidator = QRegExpValidator(commentRegex, self.ui.commentLineEdit)
		self.ui.commentLineEdit.setValidator(commentValidator)

	def updateAsset(self):
		# get the passed path & comment
		targetFilePath = self.ui.filePathLineEdit.text()
		comment = self.ui.commentLineEdit.text()
		assetUtils.updateAssetFile(self.asset, targetFilePath, comment)
		self.accept()

	def filePathDialog(self):
		containingFolder = os.path.dirname(os.path.join(assetDir, self.asset))
		diag = QFileDialog(self)
		diag.setModal(True)
		targetFilePath = diag.getOpenFileName(self,
			"Update target file",
			containingFolder,
			"Maya scene files (*.ma *.mb);;All files (*)")[0]
		print "full file path: "+targetFilePath
		# if the file path is valid
		if targetFilePath.startswith(containingFolder):
			fp = os.path.relpath(targetFilePath, containingFolder)
			self.ui.filePathLineEdit.clear()
			self.ui.filePathLineEdit.insert(fp)
		# if the file path wasn't null (user closed browser)
		elif targetFilePath:
			QMessageBox.critical(self,
				"Error", "Selected file is not within the same directory as asset file:\n"
				+ containingFolder)
