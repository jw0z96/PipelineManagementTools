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

try:
	from PipelineManagementTools import assetUtils
except ImportError:
	import assetUtils
reload(assetUtils)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class CharacterPicker(QWidget):
	def __init__(self, *args, **kwargs):
		super(CharacterPicker, self).__init__(*args, **kwargs)
		#Parent widget under Maya main window
		self.setParent(mayaMainWindow)
		self.setWindowFlags(Qt.Window)
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+'/gui/characterPicker.ui')
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# populate comboBox
		for nameSpace in cmds.namespaceInfo(lon=1):
			if nameSpace.startswith("char") and cmds.objExists(nameSpace + ":rigGroup"):
				self.ui.selectedCharacterComboBox.addItem(nameSpace)

		# connect callback for keying buttons
		self.ui.selectFacialControlsPushButton.clicked.connect(self.keyFacialControls)
		self.ui.selectBodyControlsPushButton.clicked.connect(self.keyBodyControls)
		self.ui.selectAllControlsPushButton.clicked.connect(self.selectAllControls)

	def main(self):
		self.close()
		self.show()

	def selectAllControls(self):
		selectedChar = self.ui.selectedCharacterComboBox.currentText()
		cmds.select(selectedChar + ":BODY_CTRLS_SET")
		cmds.select(selectedChar + ":FACIAL_CTRLS_SET", add = True)

	def keyFacialControls(self):
		selectedChar = self.ui.selectedCharacterComboBox.currentText()
		cmds.select(selectedChar + ":FACIAL_CTRLS_SET")

	def keyBodyControls(self):
		selectedChar = self.ui.selectedCharacterComboBox.currentText()
		cmds.select(selectedChar + ":BODY_CTRLS_SET")
