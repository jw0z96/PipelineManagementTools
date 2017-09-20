#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

import newAssetDialog
reload(newAssetDialog)

from PipelineManagementTools import assetUtils
reload(assetUtils)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class AssetManagerUI(QWidget):
	def __init__(self, parentWindow = None, *args, **kwargs):
		super(AssetManagerUI, self).__init__(parentWindow, *args, **kwargs)
		self.setWindowFlags(Qt.Window)
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/assetManager.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# department list widget callback
		self.ui.departmentListWidget.itemClicked.connect(self.departmentChanged)
		# asset list widget callback
		self.ui.assetListWidget.itemClicked.connect(self.assetChanged)
		# new asset button callback
		self.ui.newAssetPushButton.clicked.connect(self.newAssetCallback)

		# populate department list widget
		self.departmentList = [department for department in os.listdir(assetDir)
			if os.path.isdir(os.path.join(assetDir, department))
			and not department.startswith('.')]
		self.ui.departmentListWidget.addItems(self.departmentList)

	def departmentChanged(self):
		self.updateAssetWidget()

	def updateAssetWidget(self, department = None, asset = None):
		# if no department passed, get the currently selected
		if not department:
			department = self.ui.departmentListWidget.currentItem().text()
		# else get the widget to select the passed one
		else:
			self.ui.departmentListWidget.setCurrentRow(
				self.departmentList.index(department))

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

	def newAssetCallback(self):
		diag = newAssetDialog.NewAssetDialog(self)
		if diag.exec_():
			asset = diag.createdAssetFile
			department = os.path.split(asset)[0]
			self.updateAssetWidget(department, asset)
			self.assetChanged()

	def updateAssetInfo(self, asset):
		# clear the text labels
		assetDict = assetUtils.loadAssetFile(asset)
		self.ui.assetPathText.setText(asset)
		self.ui.assetMasterText.setText(assetDict['master'])
		self.ui.assetTypeText.setText(assetDict['type'])
		self.ui.assetTargetText.setText(assetDict['target'])
