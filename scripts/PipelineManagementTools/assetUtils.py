#!/usr/bin/python
import os.path
import pickle
import time

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

def createAssetFile(name, fileType, target, master, asset):
	print "CREATING ASSET:"
	print "name: " + name
	print "file type: " + fileType
	print "target file: " + target
	print "proposed master file: " + master
	print "proposed master file: " + asset

	relMaster = os.path.basename(os.path.normpath(master))
	relTarget = os.path.basename(os.path.normpath(target))

	print "relative master: " + relMaster
	print "relative target: " + relTarget

	# create the master file, a relative symlink
	os.symlink(relTarget, master)

	versionInfo = {
		'target': relTarget,
		'date': time.strftime("%c"),
		'comment': "example comment"
		}

	versionsArray = []
	versionsArray.append(versionInfo)

	# create a dict, and dump the contents to our .asset file
	assetDict = {
		'type': fileType,
		'master': relMaster,
		'currentVersion': 0,
		'versions': versionsArray
		}

	pickle.dump(assetDict, open(asset, 'wb'))

def loadAssetFile(path):
	assetPath = os.path.join(assetDir,path)
	return pickle.load(open(assetPath, 'rb'))

def updateAssetFile(asset, target):
	assetDict = loadAssetFile(asset)

	newAssetInfo = {
		'target': target,
		'date': time.strftime("%c"),
		'comment': "example comment?"
	}

	assetDict['versions'].append(newAssetInfo)
	assetDict['currentVersion'] = len(assetDict['versions'])-1

	# TODO UPDATE SYMLINK

	assetPath = os.path.join(assetDir, asset)
	pickle.dump(assetDict, open(assetPath, 'wb'))