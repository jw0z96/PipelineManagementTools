#!/usr/bin/python
import os
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

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

from gui import assetManagerUI
reload(assetManagerUI)

try:
	from PipelineManagementTools import assetUtils
except ImportError:
	import assetUtils
reload(assetUtils)

from gui import gatherDialog
reload(gatherDialog)

import maya.OpenMaya as api

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class AssetManagerMaya():
	def __init__(self, *args, **kwargs):
		self.gui = assetManagerUI.AssetManagerUI(mayaMainWindow)

		loadButton = QPushButton("Load Asset")
		loadButton.clicked.connect(self.loadSelectedAssetTarget)
		self.gui.ui.functionsHLayout.addWidget(loadButton)

		gatherButton = QPushButton("Gather Asset")
		gatherButton.clicked.connect(self.gatherSelectedAssetTarget)
		self.gui.ui.functionsHLayout.addWidget(gatherButton)

		loadVersionButton = QPushButton("Load Version")
		loadVersionButton.clicked.connect(self.loadSelectedAssetVersion)
		self.gui.ui.assetInfoHLayout.addWidget(loadVersionButton)

		# override release asset button callback
		self.gui.ui.releaseAssetPushButton.clicked.disconnect()
		self.gui.ui.releaseAssetPushButton.clicked.connect(self.releaseAssetCallback)

	def main(self):
		self.gui.show()

	def releaseAssetCallback(self):
		self.gui.releaseAssetCallback(cmds.file(q = True, sn = True))

	def loadSelectedAssetTarget(self):
		selectedAsset = self.gui.getSelectedAsset()
		if selectedAsset:
			assetDict = assetUtils.loadAssetFile(selectedAsset)
			target = assetDict['versions'][assetDict['currentVersion']]['target']
			targetRelPath = os.path.join(os.path.dirname(selectedAsset), target)
			targetAbsPath = os.path.join(assetDir, targetRelPath)
			print "loading " + targetAbsPath
			if os.path.isfile(targetAbsPath):
				cmds.file(targetAbsPath, open = True, force = True)
				# set new project directory
				print "SETTING PROJECT DIRECTORY..."
				mel.eval('setProject \"' + os.path.join(assetDir,
					os.path.dirname(selectedAsset)) + '\"')
				print "PROJECT SET TO: " + cmds.workspace(q=True, rd=True)
			else:
				QMessageBox.critical(self.gui,
				"Error",
				"File Target listed in .asset file: "
				+ targetAbsPath + " doesnt exist!")

	def loadSelectedAssetVersion(self):
		selectedAsset = self.gui.getSelectedAsset()
		version = self.gui.ui.assetInfoTableWidget.currentRow()
		if selectedAsset and version >= 0:
			assetDict = assetUtils.loadAssetFile(selectedAsset)
			target = assetDict['versions'][version]['target']
			targetRelPath = os.path.join(os.path.dirname(selectedAsset), target)
			targetAbsPath = os.path.join(assetDir, targetRelPath)
			print "loading " + targetAbsPath
			if os.path.isfile(targetAbsPath):
				cmds.file(targetAbsPath, open = True, force = True)
				# set new project directory
				print "SETTING PROJECT DIRECTORY..."
				mel.eval('setProject \"' + os.path.join(assetDir,
					os.path.dirname(selectedAsset)) + '\"')
				print "PROJECT SET TO: " + cmds.workspace(q=True, rd=True)
			else:
				QMessageBox.critical(self.gui,
				"Error",
				"File Target listed in .asset file: "
				+ targetAbsPath + " doesnt exist!")

	def gatherSelectedAssetTarget(self):
		print "referencing asset"
		selectedAsset = self.gui.getSelectedAsset()
		if selectedAsset:
			asset = assetUtils.loadAssetFile(selectedAsset)
			assetFolder = os.path.dirname(selectedAsset)
			masterFile = asset['master']
			masterPath = os.path.join(
				"$MAYA_ASSET_DIR", assetFolder, masterFile)
			diag = gatherDialog.GatherDialog(selectedAsset, masterPath, self.gui)
			if diag.exec_():
				namespace = diag.ui.nameSpaceLineEdit.text()
				if diag.ui.referenceRadioButton.isChecked():
					cmds.file(
						masterPath, r=True, namespace=namespace)
				elif diag.ui.importRadioButton.isChecked():
					cmds.file(
						masterPath, i=True, namespace=namespace)
