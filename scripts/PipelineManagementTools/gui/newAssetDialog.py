#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from PipelineManagementTools import assetUtils
reload(assetUtils)

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

		regex = QRegExp("[A-Za-z0-9_]+")
		validator = QRegExpValidator(regex, self.ui.assetNameLineEdit)
		self.ui.assetNameLineEdit.setValidator(validator)

	def createNewAsset(self):
		print "checking asset name & path"
		assetDir = os.environ['MAYA_ASSET_DIR']
		print "assetDir: "+assetDir

		newAssetName = self.ui.assetNameLineEdit.text()
		if newAssetName == '':
			QMessageBox.critical(self,
				"Error",
				"No asset name given!")
			return

		targetFilePath = self.ui.filePathLineEdit.text()
		if targetFilePath == '':
			QMessageBox.critical(self,
				"Error",
				"No file path given!")
			return

		# check if asset of name already exists
		assetList = []
		for dirpath, subdirs, files in os.walk(assetDir):
			for x in files:
				if x.endswith(".asset"):
					assetList.append(x.replace('.asset', ''))
		print assetList
		if newAssetName in assetList:
			QMessageBox.critical(self,
				"Error",
				"Asset with name '" + newAssetName + "' already exists!")
			return
		print "asset name good!"

		# check if the target file exists (if the lineEdit was edited badly)
		fullTargetFilePath = os.path.join(assetDir, targetFilePath)
		if not os.path.isfile(fullTargetFilePath):
			print "targetFilePath: " + targetFilePath + " assetDir: " + assetDir + " fullTargetFilePath: " + fullTargetFilePath
			QMessageBox.critical(self,
				"Error",
				"File: " + fullTargetFilePath + " doesnt exist!")
			return
		print "target file path good!"

		# check if the proposed master file already exists
		fileType = os.path.splitext(fullTargetFilePath)[1]
		containingFolder = os.path.dirname(fullTargetFilePath)
		proposedMasterFile = os.path.join(containingFolder, "master." + newAssetName + fileType)
		if os.path.isfile(proposedMasterFile):
			QMessageBox.critical(self,
				"Error",
				"The proposed master file: " + proposedMasterFile + " already exists")
			return

		proposedAssetFile = os.path.join(containingFolder, newAssetName + ".asset")

		assetUtils.createAssetFile(newAssetName, fileType, fullTargetFilePath, proposedMasterFile, proposedAssetFile)

		if os.path.isfile(proposedMasterFile) and os.path.isfile(proposedAssetFile):
			print "Asset created succesfully!"
			#set up variables to return
			self.createdAssetFile = os.path.relpath(proposedAssetFile, assetDir)
			self.accept()
		else:
			QMessageBox.critical(self,
				"Error",
				"Error: Asset or Master file not created, check contents of "
				+ containingFolder
				+ " or ask me what's wrong")
			return

	def validPath(self, path):
		assetDir = os.environ['MAYA_ASSET_DIR']
		return path.startswith(assetDir)

	def filePathDialog(self):
		assetDir = os.environ['MAYA_ASSET_DIR']
		diag = QFileDialog(self)
		diag.setModal(True)
		targetFilePath = diag.getOpenFileName(self,
			"Select master file",
			assetDir,
			"Maya scene files (*.ma *.mb);;All files (*)")[0]
		print "full file path: "+targetFilePath

		# if the file path is valid
		if self.validPath(targetFilePath):
			fp = os.path.relpath(targetFilePath, assetDir)
			self.ui.filePathLineEdit.clear()
			self.ui.filePathLineEdit.insert(fp)
		# if the file path wasn't null (user closed browser)
		elif targetFilePath:
			QMessageBox.critical(self, "Error", "Selected file is not within $MAYA_ASSETS_DIR:\n"+assetDir)
