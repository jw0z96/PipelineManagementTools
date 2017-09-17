#!/usr/bin/python
import os.path

class AssetManagerUI(QWidget):
	def __init__(self, parentWindow, *args, **kwargs):
		super(AssetManagerUI,self).__init__(*args, **kwargs)
		self.setParent(parentWindow)
		self.setWindowFlags( Qt.Window )
		self.initUI()

	def initUI(self):
		loader = QUiLoader()
		currentDir = os.path.dirname(__file__)
		print "oi oi saveloy" + currentDir
		file = QFile(currentDir+"/assetManager.ui")
		file.open(QFile.ReadOnly)
		self.ui = loader.load(file, parentWidget=self)
		file.close()

# def main():
# 	ui = AssetManagerUI()
# 	ui.show()
# 	return ui

# if __name__ == '__main__':
# 	main()
