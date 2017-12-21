#!/bin/bash

filesToChange=$(grep -rl --include=\*.ma 'fileInfo "license" "student"' $MAYA_ASSET_DIR)

for file in $filesToChange;
do
	echo "$file"
	sed -i 's/fileInfo "license" "student"/fileInfo "license" "education"/g' $file
done
