#!/usr/bin/python
import maya.cmds as cmds
import maya.mel as mel

mel.eval('SelectAll') # ugly mel eval to select all top level?
cmds.group(cmds.ls(sl=1), n="test_scene_export")
