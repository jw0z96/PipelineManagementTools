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

		# get the start frame and end frame from the render settings
		self.ui.startFrameSpinBox_1.setValue(cmds.getAttr('defaultRenderGlobals.startFrame'))
		self.ui.startFrameSpinBox_2.setValue(cmds.getAttr('defaultRenderGlobals.startFrame'))
		self.ui.endFrameSpinBox_1.setValue(cmds.getAttr('defaultRenderGlobals.endFrame'))
		self.ui.endFrameSpinBox_2.setValue(cmds.getAttr('defaultRenderGlobals.endFrame'))

	def main(self):
		self.close()
		self.show()

	def create_folder(self, directory):
		if not os.path.exists(directory):
			os.makedirs(directory)

	# UI CALLBACKS

	def lightingAssetChanged(self):
		# new lighting asset selected
		self.selectedAsset = self.assetList[self.ui.selectedSceneNameListWidget.currentRow()]
		self.ui.selectedSceneDirectoryTextLabel.setText(self.selectedAsset)

	def newLightingSceneCallback(self):
		cacheName = self.ui.cacheNameLineEdit_1.text()
		newSceneName = self.ui.newSceneNameLineEdit.text()

		exportAnim = self.ui.exportAnimatedCheckBox.isChecked()
		exportStatic = self.ui.exportStaticCheckBox.isChecked()

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
		self.createCaches(cacheName, self.ui.startFrameSpinBox_1.value(), self.ui.endFrameSpinBox_1.value(), exportAnim, exportStatic)

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
		if exportAnim:
			cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_animated.abc', type="string")
			cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_animated.$F4.rib', type="string")
		if exportStatic:
			cmds.setAttr('STATIC_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_static.abc', type="string")
			cmds.setAttr('STATIC_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_static.rib', type="string")

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

	def updateLightingSceneCallback(self):
		if not self.selectedAsset:
			QMessageBox.critical(self,
				"Error",
				"No lighting asset selected!")
			return

		cacheName = self.ui.cacheNameLineEdit_2.text()
		fullAssetPath = os.path.join(assetDir, self.selectedAsset)
		sceneDir = os.path.dirname(fullAssetPath)

		updateAnim = self.ui.updateAnimatedCheckBox.isChecked()
		updateStatic = self.ui.updateStaticCheckBox.isChecked()

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
		self.createCaches(cacheName, self.ui.startFrameSpinBox_2.value(), self.ui.endFrameSpinBox_2.value(), updateAnim, updateStatic)

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

		print "done"
		return

		# update the file paths for the cache nodes
		if updateAnim:
			cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_animated.abc', type="string")
			cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_animated.$F4.rib', type="string")
		if updateStatic:
			cmds.setAttr('STATIC_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_static.abc', type="string")
			cmds.setAttr('STATIC_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_static.rib', type="string")

		# increment and save scene
		mel.eval('incrementAndSaveScene 0;')

		# TODO: this is ugly, also if a user creates a new asset it's in the same directory as the first target
		assetUtils.updateAssetFile(self.selectedAsset,
			os.path.relpath(cmds.file(q=1, sn=1), sceneDir),
			"updated with cache: " + cacheName
			)

		# set time slider

		print "done!"
		self.close()

	# CACHING FUNCTIONS

	def createCaches(self, cacheName, start, end, doAnimated, doStatic):
		# directory to export into
		exportDirectory = os.path.join(self.currentProjectDir,'renderman',cacheName)
		if not os.path.exists(exportDirectory):
			os.makedirs(exportDirectory)
		# set a variable so all the textures load properly
		mel.eval('rman setvar MAYA_ASSET_DIR "$MAYA_ASSET_DIR"')

		animatedRenderableGeoList = []
		staticRenderableGeoList = []

		for mesh in cmds.ls("*_GEO", r = True):
			if cmds.objExists(mesh + ".JAY_Renderable"):
				if cmds.getAttr(mesh + ".JAY_Renderable"):
					if cmds.getAttr(mesh + ".JAY_RenderMode") == 0:
						staticRenderableGeoList.append(mesh)
					else:
						animatedRenderableGeoList.append(mesh)
				else:
					print mesh + " not being rendered"
			else:
				print mesh + " not being rendered (no attribute)"

		if(doAnimated):
			# set renderman export args
			rmanArgs = "rmanExportRIBCompression=1;rmanExportFullPaths=0;rmanExportGlobalLights=1;rmanExportLocalLights=1;rmanExportCoordinateSystems=0;rmanExportShaders=1;rmanExportAttributeBlock=0;rmanExportMultipleFrames=1;rmanExportStartFrame="+str(start)+";rmanExportEndFrame="+str(end)+";rmanExportByFrame=1"
			# select animated renderable geo
			cmds.select(animatedRenderableGeoList)
			# export rib files
			cmds.file(os.path.join(assetDir, exportDirectory, cacheName+"_animated.rib"), f=True, op=rmanArgs, type="RIB_Archive", pr=True, es=True)
			print "renderman animated export finished"
			cmds.select("*:ANIMATED_PROXY_GEO_SET")
			animatedProxyGeoList = cmds.ls(sl = 1)
			renderablesString = ""
			for renderable in list(set(animatedProxyGeoList)):
				renderablesString += " -root "
				renderablesString += str(renderable)
			# alembic export
			abcArgs = "-frameRange " + str(start) + " " + str(end) + " -writeVisibility -dataFormat hdf -uvWrite" + renderablesString + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_animated.abc"
			# abcArgs = "-frameRange " + str(start) + " " + str(end) + " -writeVisibility -dataFormat hdf -uvWrite -root chars_GRP -root props_GRP -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_animated.abc"
			cmds.AbcExport(j = abcArgs)

			# # select scalp geo
			# cmds.select("*:SCALP_GEO_SET")
			# scalpGeoList = cmds.ls(sl = 1)
			# scalpsString = ""
			# for scalpGeo in list(set(scalpGeoList)):
			# 	scalpsString += " -root "
			# 	scalpsString += str(scalpGeo)
			# # alembic export
			# abcArgs = "-frameRange " + str(start) + " " + str(end) + " -stripNamespaces -dataFormat hdf -uvWrite" + scalpsString + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_scalps.abc"

		if(doStatic):
			# set renderman export args
			rmanArgs = "rmanExportRIBCompression=1;rmanExportFullPaths=0;rmanExportGlobalLights=1;rmanExportLocalLights=1;rmanExportCoordinateSystems=0;rmanExportShaders=1;rmanExportAttributeBlock=0;rmanExportMultipleFrames=1;rmanExportStartFrame="+str(start)+";rmanExportEndFrame="+str(start)+";rmanExportByFrame=1"
			# select only the renderable geo
			cmds.select(staticRenderableGeoList)
			# export rib files
			cmds.file(os.path.join(assetDir, exportDirectory, cacheName+"_static.rib"), f=True, op=rmanArgs, type="RIB_Archive", pr=True, es=True)
			print "renderman static export finished"
			# alembic export
			abcArgs = "-frameRange " + str(start) + " " + str(start) + " -writeVisibility -dataFormat hdf -uvWrite -root assets_GRP -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_static.abc"
			cmds.AbcExport(j = abcArgs)

		# gammy workaround, use rib compile to generate the textures
		jobCompileFilePath = os.path.join(self.currentProjectDir, 'renderman', self.currentFileNameOnly, 'rib/job/jobCompile.job.rib')

		# TODO: the following error check fails if the project is set after file load, so we force a reload?
		if os.path.isfile(jobCompileFilePath):
			msgBox = QMessageBox()
			msgBox.setText("Renderman DID create this file: " + jobCompileFilePath)
			msgBox.setInformativeText("run txmake?")
			msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			msgBox.setDefaultButton(QMessageBox.Ok)
			ret = msgBox.exec_()
			if ret != QMessageBox.Ok:
				os.system("prman " + jobCompileFilePath)
		else:
			QMessageBox.critical(self,
				"Error",
				"Renderman didnt create this file: " + jobCompileFilePath)

		# group everything in the scene (alembic probably wants this unfortunately) TODO: ask user
		# mel.eval("SelectAll")
		# sceneGroup = cmds.group(n=self.currentFileNameOnly+'_GRP')

		# cmds.select("*:ANIMATED_PROXY_GEO_SET")
		# animatedProxyGeoList = cmds.ls(sl = 1)
		# renderablesString = ""
		# for renderable in list(set(animatedProxyGeoList)):
		# 	renderablesString += " -root "
		# 	renderablesString += str(renderable)

		# # renderablesString = " -root chars_GRP -root assets_GRP"

		# # alembic export
		# abcArgs = "-frameRange " + str(start) + " " + str(end) + " -writeVisibility -dataFormat hdf -uvWrite" + renderablesString + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_animated.abc"
		# # abcArgs = "-frameRange " + str(start) + " " + str(end) + " -writeVisibility -dataFormat hdf -uvWrite -root chars_GRP -file " + os.path.join(assetDir, exportDirectory, cacheName)+"_animated.abc"

		# print abcArgs

		# cmds.AbcExport(j = abcArgs)


		# abcArgs = "-frameRange " + str(start) + " " + str(end) + " -dataFormat hdf -uvWrite -root " + sceneGroup + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+".abc"
		# abcArgs = "-frameRange " + str(start) + " " + str(end) + " -dataFormat ogawa -uvWrite -root " + sceneGroup + " -file " + os.path.join(assetDir, exportDirectory, cacheName)+".abc"
		# cmds.AbcExport(j = abcArgs)
