#!/usr/bin/python
import os
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import maya.cmds as cmds

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from gui import assetManagerUI
reload(assetManagerUI)

import assetUtils
reload(assetUtils)

from gui import nameSpaceDialog
reload(nameSpaceDialog)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class AssetManagerMaya():
	def __init__(self, *args, **kwargs):
		self.gui = assetManagerUI.AssetManagerUI(mayaMainWindow)

		loadButton = QPushButton("Gather Asset")
		loadButton.clicked.connect(self.loadSelectedAssetTarget)
		self.gui.ui.functionsHLayout.addWidget(loadButton)

		referenceButton = QPushButton("Reference Asset")
		referenceButton.clicked.connect(self.referenceSelectedAssetTarget)
		self.gui.ui.functionsHLayout.addWidget(referenceButton)

		loadVersionButton = QPushButton("Load Version")
		loadVersionButton.clicked.connect(self.loadSelectedAssetVersion)
		self.gui.ui.assetInfoHLayout.addWidget(loadVersionButton)

		self.gui.currentFile = cmds.file(q = True, sn = True)

	def main(self):
		self.gui.show()

	def loadSelectedAssetTarget(self):
		selectedAsset = self.gui.getSelectedAsset()
		if selectedAsset:
			asset = assetUtils.loadAssetFile(selectedAsset)
			currentVersion = asset['currentVersion']
			assetVersions = asset['versions']
			currentVersionInfo = assetVersions[currentVersion]
			target = currentVersionInfo['target']
			targetRelPath = os.path.join(
				os.path.dirname(selectedAsset), target)
			targetAbsPath = os.path.join(assetDir, targetRelPath)
			print "loading " + targetAbsPath
			if os.path.isfile(targetAbsPath):
				cmds.file(targetAbsPath, open = True, force = True)
			else:
				QMessageBox.critical(self.gui,
				"Error",
				"File Target listed in .asset file: "
				+ targetAbsPath + " doesnt exist!")

	def loadSelectedAssetVersion(self):
		version = self.gui.ui.assetInfoTableWidget.currentRow()
		print version
		# if version >= 0:
			# print "loading " + version

	def referenceSelectedAssetTarget(self):
		print "referencing asset"
		selectedAsset = self.gui.getSelectedAsset()
		if selectedAsset:
			asset = assetUtils.loadAssetFile(selectedAsset)
			assetFolder = os.path.dirname(selectedAsset)
			masterFile = asset['master']
			referencePath = os.path.join(
				"$MAYA_ASSET_DIR", assetFolder, masterFile)
			print referencePath
			diag = nameSpaceDialog.NameSpaceDialog(referencePath, self.gui)
			if diag.exec_():
				namespace = diag.ui.nameSpaceLineEdit.text()
				cmds.file(
					referencePath, r=True, namespace=namespace)
