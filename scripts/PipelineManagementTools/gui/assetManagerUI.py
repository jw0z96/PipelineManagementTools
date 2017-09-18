#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

class AssetManagerUI(QWidget):
	def __init__(self, parentWindow, *args, **kwargs):
		super(AssetManagerUI, self).__init__(*args, **kwargs)
		# parentWindow passed to support a standalone at a later date?
		self.setParent(parentWindow)
		self.setWindowFlags(Qt.Window)
		self.initUI()

	def initUI(self):
		currentDir = os.path.dirname(__file__)
		print "running from: " + currentDir

		# load .ui file
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

	def departmentChanged(self):
		# new deparment chosen
		department = self.ui.departmentListWidget.currentItem().text()

		# clear the asset list widget
		self.ui.assetListWidget.clear()

		# assets directory specified by an environment variable
		assetDir = os.environ['MAYA_ASSET_DIR']

		# populate asset list widget
		self.assetList = []
		for dirpath, subdirs, files in os.walk(os.path.join(assetDir, department)):
			for x in files:
				if x.endswith(".asset"):
					self.assetList.append(os.path.join(dirpath, x))
					self.ui.assetListWidget.addItem(x)



# def main():
# 	ui = AssetManagerUI()
# 	ui.show()
# 	return ui

# if __name__ == '__main__':
# 	main()
