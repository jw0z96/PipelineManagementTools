#!/usr/bin/python
import os.path
import pickle
import time

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

# create a news asset file,
# which is a pickle dump of a dict of metadeta
# also creates a symlink
def createAssetFile(name, fileType, target, master, asset, comment):
	print "CREATING ASSET:"
	print "name: " + name
	print "file type: " + fileType
	print "target file: " + target
	print "proposed master file: " + master
	print "proposed master file: " + asset

	relMaster = os.path.basename(os.path.normpath(master))
	relTarget = os.path.relpath(target, os.path.dirname(master))

	print "relative master: " + relMaster
	print "relative target: " + relTarget

	# create the master file, a relative symlink
	os.symlink(relTarget, master)

	versionInfo = {
		'target': relTarget,
		'date': time.strftime("%c"),
		'comment': comment
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

# load an asset file and return a dict of it's contents
def loadAssetFile(path):
	assetPath = os.path.join(assetDir,path)
	print "assetPath: " + assetPath
	with open(assetPath, 'r') as f:
		pos = pickle.load(f)
	# return pickle.load(open(assetPath, 'rb'))
	return pos

# update an asset file with a new target file
def updateAssetFile(asset, target, comment):
	'''
	@asset: asset path relative to assetDir, e.g. lighting/shot_01/shot_01.asset
	@target: target file path relative to the directory in which the asset exists, e.g. scenes/shot_01.ma
	@comment: string comment for the version
	'''
	assetDict = loadAssetFile(asset)
	newAssetInfo = {
		'target': target,
		'date': time.strftime("%c"),
		'comment': comment
	}

	assetDict['versions'].append(newAssetInfo)
	assetDict['currentVersion'] = len(assetDict['versions'])-1

	assetPath = os.path.join(assetDir, asset)
	master = os.path.join(
		os.path.dirname(assetPath), assetDict['master']
		)

	os.unlink(master)
	os.symlink(target, master)

	pickle.dump(assetDict, open(assetPath, 'wb'))

# update the current version in a given asset file
def updateAssetVersion(asset, version):
	'''
	@asset: asset path relative to assetDir, e.g. lighting/shot_01/shot_01.asset
	@version: integer for index into version array
	'''
	assetDict = loadAssetFile(asset)
	assetDict['currentVersion'] = version
	assetPath = os.path.join(assetDir, asset)
	pickle.dump(assetDict, open(assetPath, 'wb'))

	assetVersions = assetDict['versions']
	assetPath = os.path.join(assetDir, asset)
	master = os.path.join(
		os.path.dirname(assetPath), assetDict['master']
		)

	assetVersion = assetVersions[version]
	os.unlink(master)
	os.symlink(assetVersion['target'], master)

# rebuild the symlink for a given asset file
def rebuildAssetSymlink(asset):
	'''
	@asset: asset path relative to assetDir, e.g. lighting/shot_01/shot_01.asset
	'''
	containingFolder = os.path.dirname(asset)
	assetDict = loadAssetFile(asset)
	master = assetDict['master']
	master = os.path.join(assetDir, containingFolder, master)
	target = assetDict['versions'][assetDict['currentVersion']]['target']

	print "containingFolder: " + containingFolder
	# print "assetDict: " + assetDict
	print "master: " + master
	print "target: " + target

	if os.path.isfile(master):
		print "removing: " + master
		os.remove(master)

	print "linking: " + master + " & " + target

	if os.stat(os.path.join(assetDir, containingFolder, target)).st_size == 0:
		print "WARNING, TARGET FILE IS EMPTY!!!!!!"

	os.symlink(target, master)

# def createReferenceLink(linkDir, asset):
# 	print "selected asset: " + asset
# 	assetDict = loadAssetFile(asset)
# 	masterFile = assetDict['master']
# 	assetFolder = os.path.dirname(os.path.join(assetDir, asset))
# 	relPath = os.path.relpath(
# 		assetFolder, linkDir)
# 	relMasterFile = os.path.join(relPath, masterFile)

# 	# TODO: unique asset names
# 	referenceLink = os.path.join(linkDir, 'test.ma')

# 	print "referenceLink: " + referenceLink
# 	print "relMasterFile: " + relMasterFile

# 	os.symlink(relMasterFile, referenceLink)

# 	return referenceLink
