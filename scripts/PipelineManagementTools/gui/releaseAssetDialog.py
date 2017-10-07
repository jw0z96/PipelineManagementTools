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

from PipelineManagementTools import assetUtils
reload(assetUtils)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class ReleaseAssetDialog(QDialog):
	def __init__(self, asset, currentFile, parentWindow = None, *args, **kwargs):
		super(ReleaseAssetDialog, self).__init__(parentWindow, *args, **kwargs)
		self.selectedAsset = asset
		self.currentFile = currentFile
		self.releasedAsset = None
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/releaseAssetDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		commentRegex = QRegExp("[A-Za-z0-9 _.,?!]+")
		# RELEASE NEW ASSET

		# set callbacks
		self.ui.newAssetDialogButtonBox.rejected.connect(self.close)
		self.ui.newAssetDialogButtonBox.accepted.connect(self.createNewAsset)
		self.ui.newAssetFilePathPushButton.clicked.connect(self.filePathDialog)
		# set regex for asset name
		assetNameRegex = QRegExp("[A-Za-z0-9_]+")
		assetNameValidator = QRegExpValidator(assetNameRegex, self.ui.newAssetNameLineEdit)
		self.ui.newAssetNameLineEdit.setValidator(assetNameValidator)
		# set regex for comment
		self.ui.newAssetCommentLineEdit.setValidator(
			QRegExpValidator(commentRegex, self.ui.newAssetCommentLineEdit))

		# RELEASE NEW ASSET VERSION
		if not self.selectedAsset:
			self.ui.tabWidget.removeTab(0)
			return

		# set callbacks & ui text
		self.ui.newVersionDialogButtonBox.rejected.connect(self.close)
		self.ui.newVersionDialogButtonBox.accepted.connect(self.updateAsset)

		self.ui.newVersionFilePathPushButton.clicked.connect(self.versionFilePathDialog)
		self.ui.currentAssetNameLabel.setText("Updating asset: " + self.selectedAsset)

		# check if the current file is in the selected asset dir??
		if self.currentFile:
			containingFolder = os.path.join(
				assetDir, os.path.dirname(self.selectedAsset))
			if self.currentFile.startswith(containingFolder):
				self.ui.newVersionFilePathLineEdit.setText(
					self.currentFile.lstrip(containingFolder))


		# set regex for comment
		self.ui.newVersionCommentLineEdit.setValidator(
			QRegExpValidator(commentRegex, self.ui.newVersionCommentLineEdit))

	def createNewAsset(self):
		print "checking asset name & path"
		print "assetDir: "+assetDir

		newAssetName = self.ui.newAssetNameLineEdit.text()
		if newAssetName == '':
			QMessageBox.critical(self,
				"Error",
				"No asset name given!")
			return

		targetFilePath = self.ui.newAssetFilePathLineEdit.text()
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

		# get the passed comment
		comment = self.ui.newAssetCommentLineEdit.text()
		# create a string for the .asset file
		proposedAssetFile = os.path.join(containingFolder, newAssetName + ".asset")
		# create the asset dict & file
		assetUtils.createAssetFile(
			newAssetName,
			fileType,
			fullTargetFilePath,
			proposedMasterFile,
			proposedAssetFile,
			comment
			)

		#check if the created files exist
		if os.path.isfile(proposedMasterFile) and os.path.isfile(proposedAssetFile):
			print "Asset created succesfully!"
			#set up variables to return
			self.releasedAsset = os.path.relpath(proposedAssetFile, assetDir)
			self.accept()
		else:
			QMessageBox.critical(self,
				"Error",
				"Error: Asset or Master file not created, check contents of "
				+ containingFolder
				+ " or ask me what's wrong")
			return

	def updateAsset(self):
		# get the passed path & comment
		targetFilePath = self.ui.newVersionFilePathLineEdit.text()
		comment = self.ui.newVersionCommentLineEdit.text()
		assetUtils.updateAssetFile(self.selectedAsset, targetFilePath, comment)
		self.releasedAsset = self.selectedAsset
		self.accept()

	def filePathDialog(self):
		diag = QFileDialog(self)
		diag.setModal(True)
		targetFilePath = diag.getOpenFileName(self,
			"Select target file",
			assetDir,
			"Maya scene files (*.ma *.mb);;All files (*)")[0]
		print "full file path: "+targetFilePath

		# if the file path is valid
		if targetFilePath.startswith(assetDir):
			fp = os.path.relpath(targetFilePath, assetDir)
			self.ui.newAssetFilePathLineEdit.clear()
			self.ui.newAssetFilePathLineEdit.insert(fp)
		# if the file path wasn't null (user closed browser)
		elif targetFilePath:
			QMessageBox.critical(self, "Error", "Selected file is not within $MAYA_ASSETS_DIR:\n"+assetDir)

	def versionFilePathDialog(self):
		containingFolder = os.path.dirname(os.path.join(assetDir, self.selectedAsset))
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
			self.ui.newVersionFilePathLineEdit.clear()
			self.ui.newVersionFilePathLineEdit.insert(fp)
		# if the file path wasn't null (user closed browser)
		elif targetFilePath:
			QMessageBox.critical(self,
				"Error", "Selected file is not within the same directory as asset file:\n"
				+ containingFolder)
