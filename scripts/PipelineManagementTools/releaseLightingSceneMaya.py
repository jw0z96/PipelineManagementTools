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
		self.selectedAsset = None

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

		# connect callback for new lighting scene creation
		self.ui.newScenePushButton.clicked.connect(self.newLightingSceneCallback)

		# clear the asset list widget
		self.ui.selectedSceneNameListWidget.clear()
		# populate asset list widget
		self.assetList = []
		for dirpath, subdirs, files in os.walk(os.path.join(assetDir, 'lighting')):
			for x in files:
				if x.endswith(".asset"):
					self.ui.selectedSceneNameListWidget.addItem(x)
					self.assetList.append(os.path.relpath(
						os.path.join(dirpath, x), assetDir))
		# connect callback for lighting scene selection
		self.ui.selectedSceneNameListWidget.itemClicked.connect(self.lightingAssetChanged)

		# connect callback for updating lighting scene with new caches
		self.ui.updateScenePushButton.clicked.connect(self.updateLightingSceneCallback)

	def main(self):
		self.show()

	def updateLightingSceneCallback(self):
		if not self.selectedAsset:
			QMessageBox.critical(self,
				"Error",
				"No lighting asset selected!")
			return

		cacheName = self.ui.cacheNameLineEdit_2.text()
		fullAssetPath = os.path.join(assetDir, self.selectedAsset)
		sceneDir = os.path.dirname(fullAssetPath)

		msgBox = QMessageBox()
		msgBox.setText("Caches will be sent to: " + sceneDir)
		msgBox.setInformativeText("gucci?")
		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Ok)

		ret = msgBox.exec_()

		if ret != QMessageBox.Ok:
			return

		# we reload the file, in case the project was set after file load
		cmds.file(cmds.file(q=1, sn=1), o=1, f=1)

		# print "creating caches..."
		self.createCaches(cacheName)

		print "All ok, transferring caches to: " + sceneDir
		os.system('cp -r ' + os.path.join(self.currentProjectDir, 'renderman') + ' ' + sceneDir)

		# TODO: delete the original renderman folder

		# LOAD THE LIGHTING SCENE
		assetDict = assetUtils.loadAssetFile(self.selectedAsset)
		cmds.file(os.path.join(sceneDir, assetDict['versions'][assetDict['currentVersion']]['target']), open = True, force = True)

		# set new project directory
		print "SETTING PROJECT DIRECTORY..."
		mel.eval('setProject \"' + sceneDir + '\"')
		print "PROJECT SET TO: " + cmds.workspace(q=True, rd=True)

		# update the file paths for the cache nodes
		cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'.abc', type="string")
		cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'.$F4.rib', type="string")

		# increment and save scene
		mel.eval('incrementAndSaveScene 0;')

		# TODO: this is ugly, also if a user creates a new asset it's in the same directory as the first target
		assetUtils.updateAssetFile(self.selectedAsset,
			os.path.relpath(cmds.file(q=1, sn=1), sceneDir),
			"updated with cache: " + cacheName
			)

		print "done!"
		self.close()

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

		if os.path.isdir(os.path.join(self.currentProjectDir, 'renderman')):
			msgBox1 = QMessageBox()
			msgBox1.setText("renderman export folder already exists in this project, which may not be empty... " + os.path.join(self.currentProjectDir, 'renderman'))
			msgBox1.setInformativeText("continue?")
			msgBox1.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			msgBox1.setDefaultButton(QMessageBox.Ok)
			ret = msgBox1.exec_()
			if ret != QMessageBox.Ok:
				return

		msgBox = QMessageBox()
		msgBox.setText("Asset will be created in: " + proposedSceneDir)
		msgBox.setInformativeText("gucci?")
		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Ok)

		ret = msgBox.exec_()

		if ret != QMessageBox.Ok:
			return

		# we reload the file, in case the project was set after file load
		cmds.file(cmds.file(q=1, sn=1), o=1, f=1)

		print "creating caches..."
		self.createCaches(cacheName)

		print "All ok, creating project directories"
		os.system('cp -r '+os.path.join(assetDir,'lighting/templateScene')+' '+proposedSceneDir)
		renameArg = 'mv '+os.path.join(assetDir, proposedSceneDir, 'scenes/templateScene.ma')+' '+os.path.join(assetDir, proposedSceneDir, 'scenes', newSceneName)+'.0001.ma'
		os.system(renameArg)

		print "copying caches into directory..."
		os.system("cp -r "+os.path.join(self.currentProjectDir,'renderman')+' '+proposedSceneDir+'/')

		# TODO: delete the original renderman folder

		# open new file
		cmds.file(os.path.join(assetDir, proposedSceneDir, 'scenes', newSceneName)+'.0001.ma', open = True, force = True)
		# set new project directory
		print "SETTING PROJECT DIRECTORY..."
		mel.eval('setProject \"' + proposedSceneDir + '\"')
		print "PROJECT SET TO: " + cmds.workspace(q=True, rd=True)

		# update the file paths for the cache nodes
		cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'.abc', type="string")
		cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'.$F4.rib', type="string")

		# save the file, makes it easier to query :^)
		cmds.file(save=True, type='mayaAscii')

		# TODO: this is ugly, also if a user creates a new asset it's in the same directory as the first target
		assetUtils.createAssetFile(newSceneName, '.ma',
			cmds.file(q=1, sn=1),
			os.path.join(assetDir, proposedSceneDir, 'master.' + newSceneName + '.ma'),
			os.path.join(assetDir, proposedSceneDir, newSceneName + '.asset'),
			"initial automated release of this scene"
			)

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
		# group everything in the scene (alembic probably wants this unfortunately) TODO: ask user
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

		# TODO: the following error check fails if the project is set after file load, so we force a reload?
		if os.path.isfile(jobCompileFilePath):
			os.system("prman " + jobCompileFilePath)
		else:
			QMessageBox.critical(self,
				"Error",
				"Renderman didnt create this file: " + jobCompileFilePath)

		# alembic export
		abcArgs = "-frameRange " + str(self.startFrame) + " " + str(self.endFrame) + " -dataFormat ogawa -root " + sceneGroup + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+".abc"
		cmds.AbcExport(j = abcArgs)

	def lightingAssetChanged(self):
		# new lighting asset selected
		self.selectedAsset = self.assetList[self.ui.selectedSceneNameListWidget.currentRow()]
		self.ui.selectedSceneDirectoryTextLabel.setText(self.selectedAsset)
