# -*- coding: utf-8 -*-
from direct.gui.OnscreenImage import OnscreenImage
from pandaUtils import * # helper functions
from panda3d.core import WindowProperties, ClockObject
import panda3d.core
from direct.showbase.ShowBase import ShowBase
panda3d.core.load_prc_file_data("", "show-frame-rate-meter #t")
panda3d.core.load_prc_file_data("", "sync-video #f")

class renderAR:
    def __init__(self, panda):
        self.panda = panda

        # Basic Panda3D setup:
        winProperties = WindowProperties()
        winProperties.setSize( 640, 360 )
        panda.win.requestProperties(winProperties) # applies window properties

        panda.disableMouse()
        panda.camLens.setFar(100)
        panda.camLens.setNear(0.001)
        panda.camLens.setFov(55.19465455, 42.79658875)

        # PANDA NODE LIST: mb v
        '''
        - banner (static blender model, textured cube)
        - pivotNode (dummy node, camera reparented to this node)
        - matrixNode (dummy node to apply matrix operations, gets camera HPR)
        - transNode (dummy node to apply transformations)
            - .transNodeInner (dummy node to apply transformations)
        '''
        
        # *  
        # Banner (the ring model):
        panda.banner = panda.loader.loadModel("../data/models/ring8.glb")
        panda.banner.reparentTo(panda.render) 
        panda.banner.setPos(0,0,0) # setting the model to (0,0,0) as the translations calculated are from that point
        
        #*
        #Occluder node(using a cylinder):
        panda.occluder = panda.loader.loadModel('../data/models/cylinder.glb')
        panda.occluder.reparentTo(panda.render)
        panda.occluder.setPos(0,0,0)
        panda.occluder.setScale(1.3,0.5,1.2)
        panda.occluder.clearColor()
        panda.occluder.setColor(0.611,0.533,0.44, 1)

        # **
        # Pivot (container for camera):
        panda.pivotNode = panda.render.attachNewNode("environ-pivot")
        # panda.pivotNode.setHpr(0,-90, 0) # Rotate node Pitch?
        panda.pivotNode.reparentTo(panda.render)
        # Reparent camera to pivot node:
        panda.camera.reparentTo(panda.pivotNode)
        # **

        # ***        
        # Matrix node (dummy node to apply matrix operations):
        panda.matrixNode = panda.render.attachNewNode("environ-matrix")
        # ***

        # ****
        # Trans node (dummy node to apply transformations):
        panda.transNode = panda.render.attachNewNode("environ-trans")
        # Trans node inner (dummy node to apply transformations):
        panda.transNodeInner = panda.transNode.attachNewNode("environ-trans-inner")
        # ****


        # PANDA BACKGROUND VIDEO FEED CONTAINER:
        # Prepare texture for background image object:
        cameraStreamImage = panda.cameraStreams.getColorImage() # cameraStreams.py class
        # Create Panda3D texture:
        tex = getPandaTexture(cameraStreamImage) # pandaUtils.py helper functions
        panda.bgCamImageObj = OnscreenImage(parent=panda.render2dp, image=tex) # Set background image object, for cam feed texture
        panda.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)



    # METHODS: ------------------------------------------------------------------------------------------------
    def updatePandaBackground(self, panda):
        # Update panda background texture with video feed image:
        # Get RGB image:
        cameraStreamImage = panda.cameraStreams.getColorFrame() # cameraStreams.py
        # Create Panda3D texture from RGB image:
        tex = getPandaTexture(cameraStreamImage) # pandaUtils.py
        # Apply texture to Panda3D object
        panda.bgCamImageObj.setImage(tex)


    def updateCamPos(self, panda):
        panda.occluder.setPos(panda.poseData['pandaCamPose']['trans'][0],50,panda.poseData['pandaCamPose']['trans'][2])
        panda.occluder.setHpr(panda.poseData['pandaCamPose']['rot'][0],panda.poseData['pandaCamPose']['rot'][1],panda.poseData['pandaCamPose']['rot'][2])
        panda.banner.setPos(panda.poseData['pandaCamPose']['trans'][0],50,panda.poseData['pandaCamPose']['trans'][2])
        panda.banner.setHpr(panda.poseData['pandaCamPose']['rot'][0],panda.poseData['pandaCamPose']['rot'][1],panda.poseData['pandaCamPose']['rot'][2])