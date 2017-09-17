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



echo "done!"
