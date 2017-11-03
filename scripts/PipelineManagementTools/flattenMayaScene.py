#!/usr/bin/python
import maya.cmds as cmds
import maya.mel as mel
import os

# set a variable so all the textures load properly
mel.eval('rman setvar MAYA_ASSET_DIR "$MAYA_ASSET_DIR"')

# get the start frame and end frame from the render settings
startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')

# directory to export into
exportDirectory = "/home/i7463769/MAJOR_PROJECT/3_prod/anim/shot_01/archive_test/"

# file name
fileName = "test_archive"

# set renderman export args
rmanArgs = "rmanExportRIBCompression=0;rmanExportFullPaths=0;rmanExportGlobalLights=1;rmanExportLocalLights=1;rmanExportCoordinateSystems=0;rmanExportShaders=1;rmanExportAttributeBlock=0;rmanExportMultipleFrames=1;rmanExportStartFrame="+str(startFrame)+";rmanExportEndFrame="+str(endFrame)+";rmanExportByFrame=1"

# export rib files
cmds.file(os.path.join(exportDirectory,fileName+".rib"), f=True, op=rmanArgs, type="RIB_Archive", pr=True, ea=True)

# what about textures

# alembic export
abcArgs = "-frameRange " + str(startFrame) + " " + str(endFrame) +" -ro -stripNamespaces -dataFormat ogawa -file " + os.path.join(exportDirectory,fileName+".abc")
cmds.AbcExport(j = abcArgs)
