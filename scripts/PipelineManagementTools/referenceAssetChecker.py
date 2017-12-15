#!/usr/bin/python

import maya.cmds as cmds
import os

def execute(operation):
	# assets directory specified by an environment variable
	assetDir = os.environ['MAYA_ASSET_DIR']

	# path to the assetChecker scene
	assetCheckerPath = os.path.join(assetDir, 'asset/assetChecker/assetChecker.ma')

	if operation:
		#reference it in
		cmds.file(assetCheckerPath, r=True, namespace="TEMPORARY_LIGHTING")
		print "referenced in: " + assetCheckerPath
	else:
		# dereference it
		cmds.file(assetCheckerPath, removeReference = True , f = True)
		print "dereferenced: " + assetCheckerPath
