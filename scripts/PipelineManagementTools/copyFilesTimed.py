import os
import time
import shutil

def listFiles(farmDir, shot):
	nonZeroFiles = []
	files = os.listdir(farmDir)
	for file in files:
		filePath = os.path.join(farmDir, file)
		if os.path.getsize(filePath) > 0 and file.startswith(shot):
			nonZeroFiles.append(file)
	return nonZeroFiles

def moveFiles(shot, shotFolder):
	farmDir = "/run/user/43049/gvfs/sftp:host=tete.bournemouth.ac.uk/home/i7463669/renders"
	filesToMove = listFiles(farmDir, shot)
	if len(filesToMove) > 0:
		print shot + " filesToMove " + str(filesToMove) + " to " + shotFolder
		for file in filesToMove:
			shutil.move(os.path.join(farmDir, file), os.path.join(shotFolder, file))
	else:
		print "no files to move for " + shot

def executeSomething():
	moveFiles("shot060", "/transfer/.jay/frames/shot060/shot060_lighting_cached_v.0003")
	moveFiles("shot110", "/transfer/.jay/frames/shot110/shot110_lighting_cached_v.0001")
	moveFiles("shot120", "/transfer/.jay/frames/shot120/shot120_lighting_cached_v.0003")
	time.sleep(600)

while True:
	executeSomething()
