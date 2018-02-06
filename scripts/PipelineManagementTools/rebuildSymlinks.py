#!/usr/bin/python

"""
rebuildSymlinks.py
this script should reconstruct all of the symlinks in the project
directory (e.g. master.****.ma), in the case of resilio taking a
literal shit on them (which has happened today, 02/11/2017).
"""

import assetUtils
import os

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

#list all asset files in the project directory
assetList = []
for root, subFolder, files in os.walk(assetDir):
	for item in files:
		if item.endswith(".asset"):
			assetList.append(os.path.relpath(os.path.join(root,item), assetDir))

# for asset in assetList:
# 	print asset

for asset in assetList:
	print "asset: " + asset
	assetUtils.rebuildAssetSymlink(asset)
	raw_input("Press Enter to continue...")
	os.system('clear')
