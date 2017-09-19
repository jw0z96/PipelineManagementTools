#!/usr/bin/python
import os.path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

class NewAssetDialog(QDialog):
	def __init__(self, parentWindow = None, *args, **kwargs):
		super(NewAssetDialog, self).__init__(parentWindow, *args, **kwargs)
		self.initUI()

	def initUI(self):
		currentDir = os.path.dirname(__file__)
		print "running from: " + currentDir

		# load .ui file
		file = QFile(currentDir+"/newAssetDialog.ui")
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		self.setModal(True)

