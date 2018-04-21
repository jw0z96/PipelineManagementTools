#!/usr/bin/python

"""default_outlinerGroups.py: Script to create default Maya outliner group structure for layout/animation."""

__author__	= "Yves Bedenikovic"
__date__	= "07/12/2017"

import maya.cmds as cmds

def createGroups():
	groupTitles = ["assets_GRP", "cams_GRP", "chars_GRP", "props_GRP", "fx_GRP", "lights_GRP"]
	for groupTitle in groupTitles:
		cmds.group(em = True, name = groupTitle)
