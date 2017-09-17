#!/bin/bash

mayaDir=$HOME/maya/

echo "deleting scripts"
rm -rf $mayaDir/scripts/PipelineManagentTools/
rm $mayaDir/2017/prefs/shelves/shelf_Pipeline_Tools.mel

echo "done!"