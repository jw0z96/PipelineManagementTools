#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

import newAssetDialog
reload(newAssetDialog)

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

		# assets directory specified by an environment variable
		assetDir = os.environ['MAYA_ASSET_DIR']

		# populate department list widget
		departmentList = [department for department in os.listdir(assetDir)
			if os.path.isdir(os.path.join(assetDir, department))
			and not department.startswith('.')]
		self.ui.departmentListWidget.addItems(departmentList)

		# department list widget callback
		self.ui.departmentListWidget.itemClicked.connect(self.departmentChanged)

		# asset list widget callback
		self.ui.assetListWidget.itemClicked.connect(self.assetChanged)

		# new asset button callback
		self.ui.newAssetPushButton.clicked.connect(self.newAssetCallback)

	def departmentChanged(self):
		# assets directory specified by an environment variable
		assetDir = os.environ['MAYA_ASSET_DIR']
		# clear the asset list widget & text label
		self.ui.assetListWidget.clear()
		self.ui.assetPathText.setText('')
		# new deparment chosen
		department = self.ui.departmentListWidget.currentItem().text()
		# populate asset list widget
		self.assetList = []
		for dirpath, subdirs, files in os.walk(os.path.join(assetDir, department)):
			for x in files:
				if x.endswith(".asset"):
					self.ui.assetListWidget.addItem(x)
					self.assetList.append(os.path.relpath(os.path.join(dirpath, x), assetDir))
		print self.assetList

	def assetChanged(self):
		# new asset chosen
		chosenAsset = self.assetList[self.ui.assetListWidget.currentRow()]
		print chosenAsset
		self.ui.assetPathText.setText(chosenAsset)

	def newAssetCallback(self):
		print "new asset"
		diag = newAssetDialog.NewAssetDialog(self)
		diag.show()


# def main():
# 	ui = AssetManagerUI()
# 	ui.show()
# 	return ui

# if __name__ == '__main__':
# 	main()
