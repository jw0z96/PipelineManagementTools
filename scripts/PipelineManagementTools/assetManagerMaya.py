#!/usr/bin/python
import os
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *

from gui import assetManagerUI
reload(assetManagerUI)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

def main():
	print "testing gather script"
	print os.environ['MAYA_ASSET_DIR']
	print "loading UI"
	ui = assetManagerUI.AssetManagerUI(mayaMainWindow)
	ui.show()