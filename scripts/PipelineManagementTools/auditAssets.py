#!/usr/bin/python
import os.path

import json

import maya.cmds as cmds
import maya.mel as mel

try:
	from PipelineManagementTools import assetUtils
except ImportError:
	import assetUtils
reload(assetUtils)

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

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

def getAllAssets(assetType = ""):
	# gather all assets
	assetList = []
	for dirpath, subdirs, files in os.walk(assetDir):
		for x in files:
			if x.endswith(assetType + ".asset"):
				assetList.append(os.path.relpath(os.path.join(dirpath, x), assetDir))
	return assetList

def loadAssetFileMaya(asset):
	# get asset dict
	assetDict = assetUtils.loadAssetFile(asset)
	target = assetDict['versions'][assetDict['currentVersion']]['target']
	targetRelPath = os.path.join(os.path.dirname(asset), target)
	targetAbsPath = os.path.join(assetDir, targetRelPath)
	print "loading " + targetAbsPath
	if os.path.isfile(targetAbsPath):
		cmds.file(targetAbsPath, open = True, force = True)
		# set new project directory
		print "SETTING PROJECT DIRECTORY..."
		mel.eval('setProject \"' + os.path.join(assetDir,
			os.path.dirname(asset)) + '\"')
		print "PROJECT SET TO: " + cmds.workspace(q=True, rd=True)
	else:
		print "Error, File Target listed in .asset file: doesnt exist!"

def checkAssetGeo(asset):
	loadAssetFileMaya(asset)
	badGeoList = None
	meshesList = cmds.listRelatives(cmds.ls(type = "mesh"), p=True, path=True)
	return [mesh for mesh in meshesList if not mesh.endswith("_GEO")]

def addRenderAttributesToItem(item):
	print "adding attributes to " + item
	madeChanges = False
	# whether we render or not
	if cmds.objExists(item + ".JAY_Renderable"):
		print item + ".JAY_Renderable already exists!!!!"
	else:
		cmds.addAttr(item, longName = "JAY_Renderable", attributeType = "bool")
		cmds.setAttr(item + ".JAY_Renderable", keyable = False, channelBox = True)
		madeChanges = True

	# whether its animated or static
	if cmds.objExists(item + ".JAY_RenderMode"):
		print item + ".JAY_RenderMode already exists!!!!"
	else:
		cmds.addAttr(item, longName = "JAY_RenderMode", attributeType = "enum", enumName = "Static:Animated")
		cmds.setAttr(item + ".JAY_RenderMode", keyable = False, channelBox = True)
		madeChanges = True

	return madeChanges

def addRenderAttributesToAssets():
	for buildAsset in getAllAssets("build"):
		loadAssetFileMaya(buildAsset)
		fullAssetPath = os.path.join(assetDir, buildAsset)
		sceneDir = os.path.dirname(fullAssetPath)
		meshesList = cmds.listRelatives(cmds.ls(type = "mesh", long = True, referencedNodes = False), p = True, fullPath = True)
		madeChanges = False
		for item in meshesList:
			madeChanges = madeChanges or addRenderAttributesToItem(item)

		if madeChanges:
			print "MADE CHANGES"
			msgBox = QMessageBox()
			msgBox.setText("increment and save?")
			currentAssetDict = assetUtils.loadAssetFile(buildAsset)
			currentText = currentAssetDict['versions'][currentAssetDict['currentVersion']]['comment']
			msgBox.setInformativeText("last comment: " + currentText)
			msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			msgBox.setDefaultButton(QMessageBox.Ok)
			ret = msgBox.exec_()
			if ret == QMessageBox.Ok:
				# increment and save scene
				mel.eval('incrementAndSaveScene 0;')
				try:
					assetUtils.updateAssetFile(buildAsset,
					os.path.relpath(cmds.file(q=1, sn=1), sceneDir),
					"added render attributes to mesh objects (automated)"
					)
				except IOError:
					print 'permissions error most likely'
		else:
			print "DIDNT MAKE CHANGES"

def auditAssets():
	print "------------------------------------------------------------------"
	print "AUDITING BUILD ASSETS"
	print "------------------------------------------------------------------"
	auditInfo = {}
	for buildAsset in getAllAssets("build"):
		auditInfo[buildAsset] = checkAssetGeo(buildAsset)
	print "------------------------------------------------------------------"
	print "DONE AUDIT"
	print "------------------------------------------------------------------"
	print auditInfo
	with open(os.path.join(assetDir, 'assetAudit.json'), 'w') as fp:
		json.dump(auditInfo, fp)

# auditAssets()
addRenderAttributesToAssets()
