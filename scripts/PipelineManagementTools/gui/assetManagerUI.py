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

import releaseAssetDialog
reload(releaseAssetDialog)

from PipelineManagementTools import assetUtils
reload(assetUtils)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class AssetManagerUI(QWidget):
	def __init__(self, parentWindow = None, *args, **kwargs):
		super(AssetManagerUI, self).__init__(parentWindow, *args, **kwargs)
		self.setWindowFlags(Qt.Window)
		self.initUI()
		self.selectedAsset = None

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/assetManager.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# department list widget callback
		self.ui.departmentListWidget.currentItemChanged.connect(self.departmentChanged)
		# asset list widget callback
		self.ui.assetListWidget.itemClicked.connect(self.assetChanged)
		# release asset button callback
		self.ui.releaseAssetPushButton.clicked.connect(self.releaseAssetCallback)
		# set current version button callback
		self.ui.setSelectedVersionPushButton.clicked.connect(self.setSelectedVersionCallback)

		# populate department list widget
		self.departmentList = [department for department in os.listdir(assetDir)
			if os.path.isdir(os.path.join(assetDir, department))
			and not department.startswith('.')]
		self.ui.departmentListWidget.addItems(self.departmentList)

	def releaseAssetCallback(self, currentFile = None):
		diag = releaseAssetDialog.ReleaseAssetDialog(self.selectedAsset, currentFile, self)
		if diag.exec_():
			print "diag accepted"
			asset = diag.releasedAsset
			department = os.path.split(asset)[0]
			self.updateAssetWidget(department, asset)
			self.updateAssetInfo(asset)

	def setSelectedVersionCallback(self):
		if self.selectedAsset:
			selectedVersion = self.ui.assetInfoTableWidget.currentRow()
			if selectedVersion >= 0:
				print "set selected version " + str(selectedVersion) + " as current"
				assetUtils.updateAssetVersion(self.selectedAsset, selectedVersion)
				self.updateAssetInfo()

	def updateAssetInfo(self, asset = None):
		if asset:
			self.selectedAsset = asset
		# clear the text labels
		assetDict = assetUtils.loadAssetFile(self.selectedAsset)
		self.ui.assetPathText.setText(self.selectedAsset)
		self.ui.assetMasterText.setText(assetDict['master'])
		self.ui.assetTypeText.setText(assetDict['type'])
		self.ui.assetCurrentVersionText.setText(str(assetDict['currentVersion']))

		assetVersions = assetDict['versions']
		self.ui.assetInfoTableWidget.setRowCount(len(assetVersions))

		for row in range(0, len(assetVersions)):
			assetVersion = assetVersions[row]
			self.ui.assetInfoTableWidget.setItem(row, 0, QTableWidgetItem(str(row)))
			self.ui.assetInfoTableWidget.setItem(row, 1, QTableWidgetItem(assetVersion['target']))
			self.ui.assetInfoTableWidget.setItem(row, 2, QTableWidgetItem(assetVersion['date']))
			self.ui.assetInfoTableWidget.setItem(row, 3, QTableWidgetItem(assetVersion['comment']))

	def getSelectedAsset(self):
		return self.selectedAsset

	def departmentChanged(self):
		self.updateAssetWidget()

	def updateAssetWidget(self, department = None, asset = None):
		# if no department passed, get the currently selected
		if not department:
			department = self.ui.departmentListWidget.currentItem().text()
		# else get the widget to select the passed one
		else:
			self.ui.departmentListWidget.setCurrentRow(
				self.departmentList.index(os.path.dirname(department)))

		# clear the asset list widget
		self.ui.assetListWidget.clear()
		# populate asset list widget
		self.assetList = []
		for dirpath, subdirs, files in os.walk(os.path.join(assetDir, department)):
			for x in files:
				if x.endswith(".asset"):
					self.ui.assetListWidget.addItem(x)
					self.assetList.append(os.path.relpath(
						os.path.join(dirpath, x), assetDir))

		# if an asset was passed, select it
		if asset:
			self.ui.assetListWidget.setCurrentRow(self.assetList.index(asset))

	def assetChanged(self):
		# new asset chosen
		chosenAsset = self.assetList[self.ui.assetListWidget.currentRow()]
		self.updateAssetInfo(chosenAsset)
