#!/usr/bin/python
import os
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

try:
	from PySide2.QtCore import *
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	from PySide2.QtUiTools import *
except ImportError:
	from PySide.QtCore import *
	from PySide.QtGui import *
	from PySide.QtWidgets import *
	from PySide.QtUiTools import *

try:
	from PipelineManagementTools import assetUtils
except ImportError:
	import assetUtils
reload(assetUtils)

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)

# assets directory specified by an environment variable
assetDir = os.environ['MAYA_ASSET_DIR']

class ShaderScript(QWidget):
	def __init__(self, *args, **kwargs):
		super(ShaderScript, self).__init__(*args, **kwargs)
		#Parent widget under Maya main window
		self.setParent(mayaMainWindow)
		self.setWindowFlags(Qt.Window)
		self.initUI()
		self.selectedAsset = None

	def initUI(self):
		# load .ui file
		currentDir = os.path.dirname(__file__)
		file = QFile(currentDir+'/gui/shaderScript.ui')
		file.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.ui = loader.load(file, parentWidget=self)
		file.close()

		# autofill fields

		# set regex for material name
		materialNameRegex = QRegExp("[A-Za-z0-9_]+")
		materialNameValidator = QRegExpValidator(materialNameRegex, self.ui.materialNameLineEdit)
		self.ui.materialNameLineEdit.setValidator(materialNameValidator)

		# connect callback for browse to texture folder location
		self.ui.browsePushButton.clicked.connect(self.browseTexturePath)

		# connect callback for browse to texture folder location
		self.ui.applyMaterialPushButton.clicked.connect(self.applyMaterial)

	def main(self):
		self.show()

	def browseTexturePath(self):
		self.ui.texturePathLineEdit.setText(QFileDialog.getExistingDirectory(self, "Texture folder", assetDir))

	def applyMaterial(self):
		# query material name
		materialName = self.ui.materialNameLineEdit.text()
		# material name checks
		# scene name checks
		if materialName == '':
			QMessageBox.critical(self,
				"Error",
				"No material name given!")
			return

		if cmds.objExists(materialName + '_MAT'):
			QMessageBox.critical(self,
				"Error",
				"Material already exists. Delete or Rename the current material to continue.")
			return

		# query texture path
		projectPath = self.ui.texturePathLineEdit.text()
		# path check
		if projectPath.startswith(assetDir):
			projectPath = projectPath.replace(assetDir, "$MAYA_ASSET_DIR")
		else:
			QMessageBox.critical(self,
				"Error",
				"texture location not within $MAYA_ASSET_DIR!")
			return

		# selected object
		selectedObject = cmds.ls(sl=True)

		# create shader node and MSG
		shaderNode = cmds.shadingNode('PxrSurface', asShader=True, name= materialName + '_MAT')
		shadingGroupNode = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name= materialName + '_MSG')
		# create file read nodes
		diffFileNode = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name= materialName+ '_diff_file')
		specFileNode = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name= materialName+ '_spec_file')
		roughFileNode = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name= materialName+ '_rough_file')
		dispFileNode = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name= materialName+ '_disp_file')
		# create shading utility nodes
		diffGammaNode = cmds.shadingNode('PxrGamma', asShader=True, name= materialName + '_diff_gamma')
		specGammaNode = cmds.shadingNode('PxrGamma', asShader=True, name= materialName + '_spec_gamma')
		specFloatNode = cmds.shadingNode('PxrToFloat', asShader=True, name=materialName + '_spec_float')
		dispTransformNode = cmds.shadingNode('PxrDispTransform', asShader=True, name= materialName+ '_disp_transform')
		dispNode = cmds.shadingNode('PxrDisplace', asShader=True, name= materialName+ '_disp')
		# create UV coords
		UVNode = cmds.shadingNode('place2dTexture', asShader=True, name= materialName+ '_place2dTexture')

		# connect shading nodes
		cmds.connectAttr(shaderNode + '.outColor', shadingGroupNode + '.surfaceShader')
		# _diff connections
		cmds.connectAttr(UVNode + '.outUV', diffFileNode + '.uvCoord')
		cmds.connectAttr(diffFileNode + '.outColor', diffGammaNode + '.inputRGB')
		cmds.connectAttr(diffGammaNode + '.resultRGB', shaderNode + '.diffuseColor')
		# _spec connections
		cmds.connectAttr(UVNode + '.outUV', specFileNode + '.uvCoord')
		cmds.connectAttr(specFileNode + '.outColor', specGammaNode + '.inputRGB')
		cmds.connectAttr(specGammaNode + '.resultRGB', shaderNode + '.specularFaceColor')
		cmds.connectAttr(specGammaNode + '.resultRGB', shaderNode + '.specularEdgeColor')
		cmds.connectAttr(specGammaNode + '.resultRGB', specFloatNode + '.input')
		cmds.connectAttr(specFloatNode + '.resultF', shaderNode + '.reflectionGain')
		# _rough connections
		cmds.connectAttr(UVNode + '.outUV', roughFileNode + '.uvCoord')
		cmds.connectAttr(roughFileNode + '.outAlpha', shaderNode + '.specularRoughness')
		cmds.connectAttr(roughFileNode + '.outAlpha', shaderNode + '.glassRoughness')
		# _disp connections
		cmds.connectAttr(UVNode + '.outUV', dispFileNode + '.uvCoord')
		cmds.connectAttr(dispFileNode + '.outAlpha', dispTransformNode + '.dispScalar')
		cmds.connectAttr(dispTransformNode + '.resultF', dispNode + '.dispScalar')
		cmds.connectAttr(dispNode + '.outColor', shadingGroupNode + '.displacementShader')

		# set texture Paths # TODO: check if file exists
		cmds.setAttr(diffFileNode + '.fileTextureName', os.path.join(projectPath, "%s_diff.tif" %materialName), type="string")
		cmds.setAttr(specFileNode + '.fileTextureName', os.path.join(projectPath, "%s_spec.tif" %materialName), type="string")
		cmds.setAttr(roughFileNode + '.fileTextureName', os.path.join(projectPath, "%s_rough.tif" %materialName), type="string")
		cmds.setAttr(dispFileNode + '.fileTextureName', os.path.join(projectPath, "%s_disp.tif" %materialName), type="string")

		# set node attributes
		cmds.setAttr(diffGammaNode + '.gamma', 0.454)
		cmds.setAttr(specGammaNode + '.gamma', 0.400)
		cmds.setAttr(specFloatNode + '.mode', 3)
		cmds.setAttr(roughFileNode + '.colorSpace', "Raw", type="string")
		cmds.setAttr(roughFileNode + '.alphaIsLuminance', 1)
		cmds.setAttr(dispFileNode + '.colorSpace', "Raw", type="string")
		cmds.setAttr(dispFileNode + '.alphaIsLuminance', 1)
		cmds.setAttr(dispTransformNode + '.dispRemapMode', 2)
		cmds.setAttr(dispNode + '.dispAmount', 0.15)
		cmds.setAttr(shaderNode + '.specularModelType', 1)

		## Assign Material
		cmds.select(selectedObject)
		cmds.sets(e=True, forceElement= materialName + '_MSG')
