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

class ReleaseAssetDialog(QDialog):
	def __init__(self, asset, parentWindow = None, *args, **kwargs):
		super(ReleaseAssetDialog, self).__init__(parentWindow, *args, **kwargs)
		self.selectedAsset = asset
		self.initUI()

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+"/releaseAssetDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		if not self.selectedAsset:
			self.ui.tabWidget.setTabEnabled(0, False)
