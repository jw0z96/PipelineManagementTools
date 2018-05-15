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

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+'/gui/releaseLightingSceneDialog.ui')
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# autofill fields
		self.ui.cacheNameLineEdit.setText(self.currentFileNameOnly.replace('.', '_')+'_cache')
		self.ui.selectedSceneDirectoryTextLabel.setText(self.currentProjectDir)

		# set regex for cache name
		cacheNameRegex = QRegExp("[A-Za-z0-9_]+")
		cacheNameValidator = QRegExpValidator(cacheNameRegex, self.ui.cacheNameLineEdit)
		self.ui.cacheNameLineEdit.setValidator(cacheNameValidator)

		# connect callback for updating lighting scene with new caches
		self.ui.updateScenePushButton.clicked.connect(self.updateLightingSceneCallback)

		# get the start frame and end frame from the render settings
		self.ui.startFrameSpinBox.setValue(cmds.getAttr('defaultRenderGlobals.startFrame'))
		self.ui.endFrameSpinBox.setValue(cmds.getAttr('defaultRenderGlobals.endFrame'))

	def main(self):
		self.close()
		self.show()

	def create_folder(self, directory):
		if not os.path.exists(directory):
			os.makedirs(directory)

	def updateLightingSceneCallback(self):

		cacheName = self.ui.cacheNameLineEdit.text()
		fullAssetPath = os.path.join(self.currentProjectDir, self.currentFileName)
		sceneDir = self.currentProjectDir

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
		self.createCaches(cacheName, self.ui.startFrameSpinBox.value(), self.ui.endFrameSpinBox.value(), updateAnim, updateStatic)

		# update the file paths for the cache nodes
		if updateAnim:
			cmds.setAttr('ANIM_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_animated.abc', type="string")
			cmds.setAttr('ANIM_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_animated.$F4.rib', type="string")
		if updateStatic:
			cmds.setAttr('STATIC_GPU_CACHEShape.cacheFileName', 'renderman/'+cacheName+'/'+cacheName+'_static.abc', type="string")
			cmds.setAttr('STATIC_RIB_ARCHIVEShape.filename', 'renderman/'+cacheName+'/'+cacheName+'_static.rib', type="string")

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
