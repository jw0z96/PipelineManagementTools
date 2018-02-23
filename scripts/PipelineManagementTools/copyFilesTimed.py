import os
import time
import shutil

def listFiles(farmDir):
	nonZeroFiles = []
	files = os.listdir(farmDir)
	print "files " + str(files)
	for file in files:
		filePath = os.path.join(farmDir, file)
		if os.path.getsize(filePath) > 0:
			nonZeroFiles.append(file)
	return nonZeroFiles

def executeSomething():
	farmDir = "/run/user/43049/gvfs/sftp:host=tete.bournemouth.ac.uk/home/i7463769/shot010_lighting/images"
	dstDir = "/transfer/jay/shot010_lighting_frames"
	filesToMove = listFiles(farmDir)
	print "filesToMove " + str(filesToMove)
	for file in filesToMove:
		shutil.move(os.path.join(farmDir, file), os.path.join(dstDir, file))
	#code here
	time.sleep(600)

while True:
	executeSomething()
