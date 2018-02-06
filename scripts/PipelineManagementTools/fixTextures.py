import maya.cmds as cmds

import os

assetDirs = []
assetDir = os.environ['MAYA_ASSET_DIR']
assetDirs.append(assetDir)
assetDirs.append("/Users/Alin/Desktop/3D/02-PROJECTS/jay/3_prod")

def getAllFileNodes():
	files = []
	for i in cmds.ls(type="file"):
		files.append(i)
	return files

def startsWithEnv(path):
	for uniqueAssetDir in assetDirs:
		if path.startswith(uniqueAssetDir):
			return uniqueAssetDir
	return False

def setAbsolute():
	for fileNode in getAllFileNodes():
		path = cmds.getAttr(fileNode+".fileTextureName")
		if path.startswith("$MAYA_ASSET_DIR"):
			print "this file node : " +  fileNode
			print "changed from this: " + path
			fixedPath = path.replace("$MAYA_ASSET_DIR", assetDir)
			cmds.setAttr(fileNode+".fileTextureName", fixedPath, type = "string")
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " +  fileNode
			print "it has this path: " +  path

def setRelative():
	for fileNode in getAllFileNodes():
		path = cmds.getAttr(fileNode+".fileTextureName")
		if path.startswith(assetDir):
			print "this file node : " +  fileNode
			print "changed from this: " + path
			fixedPath = path.replace(assetDir, "$MAYA_ASSET_DIR")
			cmds.setAttr(fileNode+".fileTextureName", fixedPath, type = "string")
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " + fileNode
			print "it has this path: " + path

def fixPaths():
	for fileNode in getAllFileNodes():
		path = cmds.getAttr(fileNode+".fileTextureName")
		prefix = startsWithEnv(path)
		if prefix:
			print "this file node : " +  fileNode
			print "changed from this: " + path
			fixedPath = path.replace(prefix, "$MAYA_ASSET_DIR")
			cmds.setAttr(fileNode+".fileTextureName", fixedPath, type = "string")
			print "to this: " + fixedPath
		else:
			print "this file node doesnt seem right: " + fileNode
			print "it has this path: " + path

def printAllPaths():
	for fileNode in getAllFileNodes():
		print fileNode + " " + cmds.getAttr(fileNode+".fileTextureName")
