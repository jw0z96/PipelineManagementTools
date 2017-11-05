#!/usr/bin/python
import maya.cmds as cmds
import maya.mel as mel
import os

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

# current project directory
currentProjectDir = cmds.workspace( q=True, rd=True )

# get current file name
currentFileName = cmds.file(q=1, sn=1)
fileNameOnly = os.path.splitext(os.path.basename(currentFileName))[0]

# group everything in the scene (alembic probably wants this unfortunately)
mel.eval("SelectAll")
sceneGroup = cmds.group(n=fileNameOnly)

# get the start frame and end frame from the render settings
startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')

# file name
fileName = "test_archive"

# directory to export into
exportDirectory = "anim/shot_01/renderman/test_archive"

# set renderman export args
rmanArgs = "rmanExportRIBCompression=0;rmanExportFullPaths=0;rmanExportGlobalLights=1;rmanExportLocalLights=1;rmanExportCoordinateSystems=0;rmanExportShaders=1;rmanExportAttributeBlock=0;rmanExportMultipleFrames=1;rmanExportStartFrame="+str(startFrame)+";rmanExportEndFrame="+str(endFrame)+";rmanExportByFrame=1"

# set a variable so all the textures load properly
mel.eval('rman setvar MAYA_ASSET_DIR "$MAYA_ASSET_DIR"')

# export rib files
cmds.file(os.path.join(assetDir, exportDirectory,fileName+".rib"), f=True, op=rmanArgs, type="RIB_Archive", pr=True, ea=True)

# gammy workaround, use rib compile to generate the textures
jobCompileFilePath = os.path.join(currentProjectDir, 'renderman', fileNameOnly, 'rib/job/jobCompile.job.rib')
os.system("prman " + jobCompileFilePath)

# alembic export
# this was a callback from a normal alembic export
# AbcExport -j "-frameRange 1 120 -dataFormat ogawa -root |SHOT01_LIGHTING -file /home/jw0z/MAJOR_PROJECT/3_prod/anim/shot_01/cache/alembic/test.abc";

abcArgs = "-frameRange " + str(startFrame) + " " + str(endFrame) + " -dataFormat ogawa -root " + sceneGroup + " -file " + os.path.join(assetDir, exportDirectory, fileName)+".abc"

cmds.AbcExport(j = abcArgs)

print "done"
