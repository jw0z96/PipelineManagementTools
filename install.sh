#!/bin/bash

mayaScriptDir=$HOME/maya/scripts

if [ -d $mayaScriptDir ]; then
	echo "copying scripts!"
	cp -r scripts/PipelineManagementTools/ $mayaScriptDir
else
	echo "can't find maya scripts directory!"
fi

mayaShelfDir=$HOME/maya/2017/prefs/shelves

if [ -d $mayaShelfDir ]; then
	echo "copying shelves!"
	cp scripts/shelf_Pipeline_Tools.mel $mayaShelfDir
else
	echo "can't find maya shelves directory!"
fi

mayaPrefsDir=$HOME/maya/2017/prefs

if [ -d $mayaPrefsDir ]; then
	echo "copying icons!"
	cp -r scripts/PipelineManagementTools/gui/icons/ $mayaPrefsDir
else
	echo "can't find maya prefs directory!"
fi

echo "done!"
