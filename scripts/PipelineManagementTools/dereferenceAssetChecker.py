#!/usr/bin/python

import maya.cmds as cmds
import os

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

# path to the assetChecker scene
assetCheckerPath = os.path.join(assetDir, 'asset/assetChecker/assetChecker.ma')

# dereference it
cmds.file(assetCheckerPath, removeReference = True , f = True)

print "dereferenced: " + assetCheckerPath
