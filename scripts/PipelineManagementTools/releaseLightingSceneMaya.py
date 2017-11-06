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

class ReleaseLightingSceneMaya(QWidget):
	def __init__(self, *args, **kwargs):
		super(ReleaseLightingSceneMaya, self).__init__(*args, **kwargs)
		#Parent widget under Maya main window
		self.setParent(mayaMainWindow)
		self.setWindowFlags(Qt.Window)
		self.getCurrentSceneInfo()
		self.initUI()

	def getCurrentSceneInfo(self):
		# current project directory
		self.currentProjectDir = cmds.workspace( q=True, rd=True )
		# get current file name
		self.currentFileName = cmds.file(q=1, sn=1)
		self.currentFileNameOnly = os.path.splitext(os.path.basename(self.currentFileName))[0]
		# get the start frame and end frame from the render settings
		self.startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
		self.endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+'/gui/releaseLightingSceneDialog.ui')
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# autofill fields
		self.ui.cacheNameLineEdit_1.setText(self.currentFileNameOnly.replace('.', '_')+'_cache')
		self.ui.cacheNameLineEdit_2.setText(self.currentFileNameOnly.replace('.', '_')+'_cache')

		# set regex for cache name
		cacheNameRegex = QRegExp("[A-Za-z0-9_]+")
		cacheNameValidator = QRegExpValidator(cacheNameRegex, self.ui.cacheNameLineEdit_1)
		self.ui.cacheNameLineEdit_1.setValidator(cacheNameValidator)
		cacheNameValidator = QRegExpValidator(cacheNameRegex, self.ui.cacheNameLineEdit_2)
		self.ui.cacheNameLineEdit_2.setValidator(cacheNameValidator)

		# set regex for scene name
		sceneNameRegex = QRegExp("[A-Za-z0-9_]+")
		sceneNameValidator = QRegExpValidator(sceneNameRegex, self.ui.newSceneNameLineEdit)
		self.ui.newSceneNameLineEdit.setValidator(sceneNameValidator)

		self.ui.newScenePushButton.clicked.connect(self.newLightingSceneCallback)

	def main(self):
		self.show()

	def newLightingSceneCallback(self):
		cacheName = self.ui.cacheNameLineEdit_1.text()
		newSceneName = self.ui.newSceneNameLineEdit.text()

		# scene name checks
		if newSceneName == '':
			QMessageBox.critical(self,
				"Error",
				"No scene name given!")
			return
		# proposed scene directory
		proposedSceneDir = os.path.join(assetDir, 'lighting', newSceneName)
		if os.path.isdir(proposedSceneDir):
			QMessageBox.critical(self,
				"Error",
				"Asset folder already exists! " + proposedSceneDir)
			return

		msgBox = QMessageBox()
		msgBox.setText("Asset wil be created in: " + proposedSceneDir)
		msgBox.setInformativeText("gucci?")
		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Ok)

		ret = msgBox.exec_()

		if ret != QMessageBox.Ok:
			return

		print "creating caches..."
		self.createCaches(cacheName)

		print "All ok, creating project directories"
		os.system('cp -r '+os.path.join(assetDir,'lighting/templateScene')+' '+proposedSceneDir)
		renameArg = 'mv '+os.path.join(assetDir, proposedSceneDir, 'scenes/templateScene.ma')+' '+os.path.join(assetDir, proposedSceneDir, 'scenes', newSceneName)+'.0001.ma'
		print renameArg
		os.system(renameArg)

		print "copying caches into directory..."
		os.system("cp -r "+os.path.join(self.currentProjectDir,'renderman')+' '+proposedSceneDir+'/')

		# open new file
		cmds.file(os.path.join(assetDir, proposedSceneDir, 'scenes', newSceneName)+'.0001.ma', open = True, force = True)
		# set new project directory
		# cmds.workspace(dir = proposedSceneDir)
		mel.eval('setProject \"' + proposedSceneDir + '\"')
		print cmds.workspace(q=True, rd=True)

		cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'.abc', type="string")
		cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'.$F4.rib', type="string")

		cmds.file(save=True, type='mayaAscii')
		print "done!"
		self.close()

	def create_folder(self, directory):
		if not os.path.exists(directory):
			os.makedirs(directory)

	def createCaches(self, cacheName):
		# directory to export into
		exportDirectory = os.path.join(self.currentProjectDir,'renderman',cacheName)
		if not os.path.exists(exportDirectory):
			os.makedirs(exportDirectory)
		# group everything in the scene (alembic probably wants this unfortunately) TODO, ASK USER
		mel.eval("SelectAll")
		sceneGroup = cmds.group(n=self.currentFileNameOnly+'_GRP')
		# set a variable so all the textures load properly
		mel.eval('rman setvar MAYA_ASSET_DIR "$MAYA_ASSET_DIR"')
		# set renderman export args
		rmanArgs = "rmanExportRIBCompression=0;rmanExportFullPaths=0;rmanExportGlobalLights=1;rmanExportLocalLights=1;rmanExportCoordinateSystems=0;rmanExportShaders=1;rmanExportAttributeBlock=0;rmanExportMultipleFrames=1;rmanExportStartFrame="+str(self.startFrame)+";rmanExportEndFrame="+str(self.endFrame)+";rmanExportByFrame=1"
		# export rib files
		cmds.file(os.path.join(assetDir, exportDirectory, cacheName+".rib"), f=True, op=rmanArgs, type="RIB_Archive", pr=True, ea=True)
		# gammy workaround, use rib compile to generate the textures
		jobCompileFilePath = os.path.join(self.currentProjectDir, 'renderman', self.currentFileNameOnly, 'rib/job/jobCompile.job.rib')
		os.system("prman " + jobCompileFilePath)
		# alembic export
		abcArgs = "-frameRange " + str(self.startFrame) + " " + str(self.endFrame) + " -dataFormat ogawa -root " + sceneGroup + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+".abc"
		cmds.AbcExport(j = abcArgs)
