#!/bin/bash

print_zero_file () {
	# echo "$1 is 0 bytes"
	archive=".sync/Archive"
	fullPath=$archive/$1

	if [ -f "$fullPath" ]; then
        echo "$1 FOUND in archive."
	else
		echo "$1 NOT in archive"
		# echo " "
	fi
}

export -f print_zero_file

currentdir=$(pwd)
dir=$MAYA_ASSET_DIR
parentdir=$(dirname $dir)

cd $parentdir

pwd

find . -size 0 -exec bash -c 'print_zero_file "$0"' {} \;

cd $currentdir
