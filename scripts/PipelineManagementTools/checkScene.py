import maya.cmds as cmds

renderableAnimatedGeo = []
renderableStaticGeo = []
notRenderableGeo = []
notAttributeGeo = []

for mesh in cmds.ls("*_GEO", r = True):
	if cmds.objExists(mesh + ".JAY_Renderable"):
		if cmds.getAttr(mesh + ".JAY_Renderable"):
			if cmds.getAttr(mesh + ".JAY_RenderMode") == 0:
				renderableStaticGeo.append(mesh)
			else:
				renderableAnimatedGeo.append(mesh)
		else:
			notRenderableGeo.append(mesh)
	else:
		notAttributeGeo.append(mesh)

print '====================================='
print '       RENDERABLE ANIMATED GEO       '
print '====================================='
for x in renderableAnimatedGeo:
	print x
print '====================================='
print ''
print '====================================='
print '        RENDERABLE STATIC GEO        '
print '====================================='
for x in renderableStaticGeo:
	print x
print '====================================='
print ''
print '====================================='
print '         NOT RENDERABLE GEO          '
print '====================================='
for x in notRenderableGeo:
	print x
print '====================================='
print ''
print '====================================='
print '          NO ATTRIBUTE GEO           '
print '====================================='
for x in notAttributeGeo:
	print x
print '====================================='
print ''
print '====================================='
print '           BADLY NAMED GEO           '
print '====================================='
for x in cmds.listRelatives(cmds.ls(type = "mesh"), p=True, path=True):
	if not x.endswith("_GEO"):
		print x
print '====================================='
