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

		# set regex for material name
		materialNameRegex = QRegExp("[A-Za-z0-9_]+")
		materialNameValidator = QRegExpValidator(materialNameRegex, self.ui.materialNameLineEdit)
		self.ui.materialNameLineEdit.setValidator(materialNameValidator)

		# connect callback for browse to texture folder location
		self.ui.pathToolButton.clicked.connect(self.browseTexturePathCallback)

		# connect callback for browse to texture folder location
		self.ui.applyMaterialPushButton.clicked.connect(self.applyMaterial)

	def main(self):
		self.close()
		self.show()

	def clearUI(self):
		self.ui.pathLabel.setText("None")
		self.ui.materialNameLineEdit.setText("")

		self.ui.diffusePathLabel.setText("None")
		self.ui.diffuseCheckBox.setCheckable(False)
		self.ui.diffuseCheckBox.setChecked(False)

		self.ui.displacementPathLabel.setText("None")
		self.ui.displacementCheckBox.setCheckable(False)
		self.ui.displacementCheckBox.setChecked(False)

		self.ui.roughnessPathLabel.setText("None")
		self.ui.roughnessCheckBox.setCheckable(False)
		self.ui.roughnessCheckBox.setChecked(False)

		self.ui.specularPathLabel.setText("None")
		self.ui.specularCheckBox.setCheckable(False)
		self.ui.specularCheckBox.setChecked(False)

		self.ui.triplanarCheckbox.setChecked(False)

	def browseTexturePathCallback(self):
		chosenTexture = QFileDialog.getOpenFileName(self, "Update target file", assetDir, "Textures (*.tif *.tiff);;All files (*)")[0]

		# the dialog was closed
		if not chosenTexture:
			self.clearUI()

		# path check & get absolute path
		if chosenTexture.startswith(assetDir):
			chosenTexture = os.path.relpath(chosenTexture, assetDir)
		else:
			QMessageBox.critical(self,
				"Error",
				"texture location not within $MAYA_ASSET_DIR!")
			self.clearUI()
			return

		# get the chosen directory, file name, and file type
		chosenDirectory, chosenFileName = os.path.split(chosenTexture)
		chosenFileName, chosenFileType = os.path.splitext(chosenFileName)

		# strip the texture type
		chosenFileName = chosenFileName.replace("_diff", "")
		chosenFileName = chosenFileName.replace("_disp", "")
		chosenFileName = chosenFileName.replace("_rough", "")
		chosenFileName = chosenFileName.replace("_spec", "")

		print "chosenDirectory " + chosenDirectory
		print "chosenFileName " + chosenFileName
		print "chosenFileType " + chosenFileType

		# check for diffuse file and autofill
		diffFile = None
		diffFilePath = os.path.join(chosenDirectory, chosenFileName + "_diff" + chosenFileType)
		if os.path.isfile(os.path.join(assetDir, diffFilePath)):
			diffFile = diffFilePath
			self.ui.diffusePathLabel.setText(diffFile)
			self.ui.diffuseCheckBox.setCheckable(True)
			self.ui.diffuseCheckBox.setChecked(True)

		# check for displacement file and autofill
		dispFile = None
		dispFilePath = os.path.join(chosenDirectory, chosenFileName + "_disp" + chosenFileType)
		if os.path.isfile(os.path.join(assetDir, dispFilePath)):
			dispFile = dispFilePath
			self.ui.displacementPathLabel.setText(dispFile)
			self.ui.displacementCheckBox.setCheckable(True)
			self.ui.displacementCheckBox.setChecked(True)

		# check for roughness file and autofill
		roughFile = None
		roughFilePath = os.path.join(chosenDirectory, chosenFileName + "_rough" + chosenFileType)
		if os.path.isfile(os.path.join(assetDir, roughFilePath)):
			roughFile = roughFilePath
			self.ui.roughnessPathLabel.setText(roughFile)
			self.ui.roughnessCheckBox.setCheckable(True)
			self.ui.roughnessCheckBox.setChecked(True)

		# check for specular file and autofill
		specFile = None
		specFilePath = os.path.join(chosenDirectory, chosenFileName + "_spec" + chosenFileType)
		if os.path.isfile(os.path.join(assetDir, specFilePath)):
			specFile = specFilePath
			self.ui.specularPathLabel.setText(specFile)
			self.ui.specularCheckBox.setCheckable(True)
			self.ui.specularCheckBox.setChecked(True)

		# autofill path label
		self.ui.pathLabel.setText(os.path.join(chosenDirectory, chosenFileName))
		# autofill material name
		self.ui.materialNameLineEdit.setText(chosenFileName)

	def applyMaterial(self):
		# query material name
		materialName = self.ui.materialNameLineEdit.text()
		# material name checks
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

		# get selected object
		selectedObject = cmds.ls(sl=True)
		if not selectedObject: # TODO: give the option to create shader without assigning
			msgBox1 = QMessageBox()
			msgBox1.setText("No object selected to assign material to")
			msgBox1.setInformativeText("continue?")
			msgBox1.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
			msgBox1.setDefaultButton(QMessageBox.Ok)
			ret = msgBox1.exec_()
			if ret != QMessageBox.Ok:
				return

		# get all of the checkbox states
		diffuseChecked = self.ui.diffuseCheckBox.isChecked()
		displacementChecked = self.ui.displacementCheckBox.isChecked()
		roughnessChecked = self.ui.roughnessCheckBox.isChecked()
		specularChecked = self.ui.specularCheckBox.isChecked()
		triplanarChecked = self.ui.triplanarCheckbox.isChecked()

		# check that at least one is checked...
		if not diffuseChecked and not displacementChecked and not roughnessChecked and not specularChecked:
			QMessageBox.critical(self,
				"Error",
				"None of the texture channels are checked")
			return

		diffusePath = self.ui.diffusePathLabel.text()
		displacementPath = self.ui.displacementPathLabel.text()
		roughnessPath = self.ui.roughnessPathLabel.text()
		specularPath = self.ui.specularPathLabel.text()

		# create shader node and MSG
		shaderNode = cmds.shadingNode('PxrSurface', asShader = True, name = materialName + '_MAT')
		shadingGroupNode = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = materialName + '_MSG')

		# create UV coords or Triplanar projection
		UVNode = None
		if triplanarChecked:
			UVNode = cmds.shadingNode('PxrRoundCube', asShader=True, name= materialName+ '_roundCube')
			cmds.setAttr(UVNode + '.randomOrientation', 1)
			cmds.setAttr(UVNode + '.randomOffset', 1)
			cmds.setAttr(UVNode + '.randomFlip', 1)
			cmds.setAttr(UVNode + '.transitionWidth', 0.65)
		else:
			UVNode = cmds.shadingNode('place2dTexture', asShader = True, name = materialName + '_place2dTexture')

		# connect shading nodes
		cmds.connectAttr(shaderNode + '.outColor', shadingGroupNode + '.surfaceShader')
		# set node attributes
		cmds.setAttr(shaderNode + '.specularModelType', 1)

		# DIFFUSE

		if diffuseChecked:
			# create utility nodes
			diffHSLNode = cmds.shadingNode('PxrHSL', asShader=True, name = materialName + '_diff_HSL')
			# connect attributes
			cmds.connectAttr(diffHSLNode + '.resultRGB', shaderNode + '.diffuseColor' )
			cmds.connectAttr(diffHSLNode + '.resultRGB', shaderNode + '.subsurfaceColor' )
			cmds.connectAttr(diffHSLNode + '.resultRGB', shaderNode + '.singlescatterColor' )

			if triplanarChecked:
				# create file read nodes
				diffTriplanarNode = cmds.shadingNode('PxrMultiTexture', asShader=True, name = materialName + '_diff_triplanar')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(diffTriplanarNode + '.filename0', os.path.join("$MAYA_ASSET_DIR", diffusePath), type = "string")
				# set node attributes
				cmds.setAttr(diffTriplanarNode + '.linearize', 1)
				cmds.setAttr(diffTriplanarNode + '.filter', 5)
				# connect attributes
				cmds.connectAttr(UVNode + '.resultMulti', diffTriplanarNode + '.manifoldMulti' )
				cmds.connectAttr(diffTriplanarNode + '.resultRGB', diffHSLNode + '.inputRGB' )
			else:
				# create file read nodes
				diffFileNode = cmds.shadingNode('file', asTexture = True, isColorManaged = True, name = materialName + '_diff_file')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(diffFileNode + '.fileTextureName', os.path.join("$MAYA_ASSET_DIR", diffusePath), type = "string")
				# create shading utility nodes
				diffGammaNode = cmds.shadingNode('PxrGamma', asShader = True, name = materialName + '_diff_gamma')
				# set node attributes
				cmds.setAttr(diffGammaNode + '.gamma', 0.454)
				# connect attributes
				cmds.connectAttr(UVNode + '.outUV', diffFileNode + '.uvCoord')
				cmds.connectAttr(diffFileNode + '.outColor', diffGammaNode + '.inputRGB')
				cmds.connectAttr(diffGammaNode + '.resultRGB', diffHSLNode + '.inputRGB')

		# DISPLACEMENT

		if displacementChecked:
			# create utility nodes
			dispTransformNode = cmds.shadingNode('PxrDispTransform', asShader = True, name = materialName+ '_disp_transform')
			dispNode = cmds.shadingNode('PxrDisplace', asShader = True, name = materialName+ '_disp')
			# set node attributes
			cmds.setAttr(dispTransformNode + '.dispRemapMode', 2)
			# connect attributes
			cmds.connectAttr(dispTransformNode + '.resultF', dispNode + '.dispScalar')
			cmds.connectAttr(dispNode + '.outColor', shadingGroupNode + '.displacementShader')

			if triplanarChecked:
				# create file read nodes
				dispTriplanarNode = cmds.shadingNode('PxrMultiTexture', asShader=True, name= materialName+ '_disp_triplanar')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(dispTriplanarNode + '.filename0', os.path.join("$MAYA_ASSET_DIR", displacementPath), type = "string")
				# set node attributes
				cmds.setAttr(dispNode + '.dispAmount', 0.01)
				# connect attributes
				cmds.connectAttr(UVNode + '.resultMulti', dispTriplanarNode + '.manifoldMulti' )
				cmds.connectAttr(dispTriplanarNode + '.resultA', dispTransformNode + '.dispScalar')

			else:
				# create file read nodes
				dispFileNode = cmds.shadingNode('file', asTexture = True, isColorManaged = True, name = materialName + '_disp_file')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(dispFileNode + '.fileTextureName', os.path.join("$MAYA_ASSET_DIR", displacementPath), type = "string")
				# set node attributes
				cmds.setAttr(dispFileNode + '.colorSpace', "Raw", type = "string")
				cmds.setAttr(dispFileNode + '.alphaIsLuminance', 1)
				cmds.setAttr(dispNode + '.dispAmount', 0.15)
				# connect attributes
				cmds.connectAttr(UVNode + '.outUV', dispFileNode + '.uvCoord')
				cmds.connectAttr(dispFileNode + '.outAlpha', dispTransformNode + '.dispScalar')

		# ROUGHNESS

		if roughnessChecked:
			# create utility nodes
			roughRemapNode = cmds.shadingNode('PxrRemap', asShader = True, name = materialName + '_rough_remap')
			roughFloatNode = cmds.shadingNode('PxrToFloat', asShader = True, name = materialName + '_rough_float')
			# set node attributes
			cmds.setAttr(roughFloatNode + '.mode', 3)
			# connect attributes
			cmds.connectAttr(roughRemapNode + '.resultRGB', roughFloatNode + '.input')
			cmds.connectAttr(roughFloatNode + '.resultF', shaderNode + '.specularRoughness' )
			cmds.connectAttr(roughFloatNode + '.resultF', shaderNode + '.glassRoughness' )

			if triplanarChecked:
				# create file read nodes
				roughTriplanarNode = cmds.shadingNode('PxrMultiTexture', asShader = True, name = materialName + '_rough_triplanar')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(roughTriplanarNode + '.filename0', os.path.join("$MAYA_ASSET_DIR", roughnessPath), type = "string")
				# set node attributes
				cmds.setAttr(roughTriplanarNode + '.filter', 5)
				# connect attributes
				cmds.connectAttr(UVNode + '.resultMulti', roughTriplanarNode + '.manifoldMulti')
				cmds.connectAttr(roughTriplanarNode + '.resultRGB', roughRemapNode + '.inputRGB' )
			else:
				# create file read nodes
				roughFileNode = cmds.shadingNode('file', asTexture = True, isColorManaged = True, name = materialName + '_rough_file')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(roughFileNode + '.fileTextureName', os.path.join("$MAYA_ASSET_DIR", roughnessPath), type = "string")
				# set node attributes
				cmds.setAttr(roughFileNode + '.colorSpace', "Raw", type = "string")
				cmds.setAttr(roughFileNode + '.alphaIsLuminance', 1)
				# connect attributes
				cmds.connectAttr(UVNode + '.outUV', roughFileNode + '.uvCoord')
				cmds.connectAttr(roughFileNode + '.outColor', roughRemapNode + '.inputRGB')

		# SPECULAR

		if specularChecked:
			# create utility nodes
			specHSLNode = cmds.shadingNode('PxrHSL', asShader = True, name = materialName + '_spec_HSL')
			specFloatNode = cmds.shadingNode('PxrToFloat', asShader = True, name = materialName + '_spec_float')
			# set node attributes
			cmds.setAttr(specFloatNode + '.mode', 3)
			# connect attributes
			cmds.connectAttr(specHSLNode + '.resultRGB', shaderNode + '.specularFaceColor')
			cmds.connectAttr(specHSLNode + '.resultRGB', shaderNode + '.specularEdgeColor')
			cmds.connectAttr(specHSLNode + '.resultRGB', specFloatNode + '.input')
			cmds.connectAttr(specFloatNode + '.resultF', shaderNode + '.reflectionGain')

			if triplanarChecked:
				# create file read nodes
				specTriplanarNode = cmds.shadingNode('PxrMultiTexture', asShader=True, name = materialName + '_spec_triplanar')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(specTriplanarNode + '.filename0', os.path.join("$MAYA_ASSET_DIR", specularPath), type = "string")
				# set node attributes
				cmds.setAttr(specTriplanarNode + '.linearize', 1)
				cmds.setAttr(specTriplanarNode + '.filter', 5)
				# connect attributes
				cmds.connectAttr(UVNode + '.resultMulti', specTriplanarNode + '.manifoldMulti' )
				cmds.connectAttr(specTriplanarNode + '.resultRGB', specHSLNode + '.inputRGB' )
			else:
				# create file read nodes
				specFileNode = cmds.shadingNode('file', asTexture = True, isColorManaged = True, name = materialName + '_spec_file')
				# set texture Paths # TODO: check if file exists
				cmds.setAttr(specFileNode + '.fileTextureName', os.path.join("$MAYA_ASSET_DIR", specularPath), type = "string")
				# create shading utility nodes
				specGammaNode = cmds.shadingNode('PxrGamma', asShader = True, name = materialName + 'spec_gamma')
				# set node attributes
				cmds.setAttr(specGammaNode + '.gamma', 0.454)
				# connect attributes
				cmds.connectAttr(UVNode + '.outUV', specFileNode + '.uvCoord')
				cmds.connectAttr(specFileNode + '.outColor', specGammaNode + '.inputRGB')
				cmds.connectAttr(specGammaNode + '.resultRGB', specHSLNode + '.inputRGB')

		# assign Material
		if selectedObject:
			cmds.select(selectedObject)
			cmds.sets(e = True, forceElement = materialName + '_MSG')
