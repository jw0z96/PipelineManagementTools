import maya.cmds as cmds
import maya.mel as mel

import os

assetDirs = []
assetDir = os.environ['MAYA_ASSET_DIR']
assetDirs.append(assetDir)
assetDirs.append("/Users/Alin/Desktop/3D/02-PROJECTS/jay/3_prod")
assetDirs.append("/home/i7463669/Documents/jay/3_prod")

def getAllFileNodes():
	files = []
	for i in cmds.ls(type="file"):
		files.append(i)
	for j in cmds.ls(type="PxrMultiTexture"):
		files.append(j)
	return files

def startsWithEnv(path):
	for uniqueAssetDir in assetDirs:
		if path.startswith(uniqueAssetDir):
			return uniqueAssetDir
	return False

def setAbsolute():
	for fileNode in getAllFileNodes():
		attr = ".fileTextureName"
		if cmds.objectType(fileNode) == "PxrMultiTexture":
			attr = ".filename0"
		path = cmds.getAttr(fileNode+attr)
		print "================================================================"
		if path.startswith("$MAYA_ASSET_DIR"):
			print "this file node : " +  fileNode
			print "----------------------------------------------------------------"
			print "changed from this: " + path
			fixedPath = path.replace("$MAYA_ASSET_DIR", assetDir)
			cmds.setAttr(fileNode+attr, fixedPath, type = "string")
			print "----------------------------------------------------------------"
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " +  fileNode
			print "----------------------------------------------------------------"
			print "it has this path: " +  path
		print "================================================================"


def setRelative():
	for fileNode in getAllFileNodes():
		attr = ".fileTextureName"
		if cmds.objectType(fileNode) == "PxrMultiTexture":
			attr = ".filename0"
		path = cmds.getAttr(fileNode+attr)
		print "================================================================"
		if path.startswith(assetDir):
			print "this file node : " +  fileNode
			print "----------------------------------------------------------------"
			print "changed from this: " + path
			print "----------------------------------------------------------------"
			fixedPath = path.replace(assetDir, "$MAYA_ASSET_DIR")
			cmds.setAttr(fileNode+attr, fixedPath, type = "string")
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " + fileNode
			print "----------------------------------------------------------------"
			print "it has this path: " + path
		print "================================================================"


def fixPaths():
	for fileNode in getAllFileNodes():
		attr = ".fileTextureName"
		if cmds.objectType(fileNode) == "PxrMultiTexture":
			attr = ".filename0"
		path = cmds.getAttr(fileNode+attr)
		print "================================================================"
		prefix = startsWithEnv(path)
		if prefix:
			print "----------------------------------------------------------------"
			print "this file node : " +  fileNode
			print "----------------------------------------------------------------"
			print "changed from this: " + path
			fixedPath = path.replace(prefix, "$MAYA_ASSET_DIR")
			cmds.setAttr(fileNode+attr, fixedPath, type = "string")
			print "----------------------------------------------------------------"
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " + fileNode
			print "it has this path: " + path
		print "================================================================"

def printAllPaths():
	for fileNode in getAllFileNodes():
		print "================================================================"
		print fileNode
		print "----------------------------------------------------------------"
		attr = ".fileTextureName"
		if cmds.objectType(fileNode) == "PxrMultiTexture":
			attr = ".filename0"
		print cmds.getAttr(fileNode+attr)
		print "================================================================"

def generateAllPreviews():
	for fileNode in getAllFileNodes():
		if cmds.objectType(fileNode) == "file" and cmds.getAttr(fileNode + ".uvTilingMode") == 3:
			print "================================================================"
			print "generating UDIM previews for " + fileNode
			mel.eval('generateUvTilePreview ' + fileNode)
			print "================================================================"
