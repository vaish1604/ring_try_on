# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
from direct.showbase.ShowBase import ShowBase # Panda3D
from renderAR import * # panda AR renderer
from pandaUtils import * # helper functions
from cameraStreams import cameraStreams # class
from handPose import poseEstimation # class
import simplepbr
print('- Start -')

class MainApp(ShowBase):    
    def __init__(self):
        ShowBase.__init__(self)
        # simpepbr.init()
        # POSE ESTIMATION DATA (updated in handPose.py):
        self.poseData = {
            'pandaCamPose': { # Camera pose in the panda world (calculated from ArUco marker data):
                'trans' : [], # x,y,z
                'rot'   : []  # h,p,r
            }
        }
        # CAMERA/VIDEO STREAM SETUP:
        self.cameraStreams = cameraStreams() # cameraStreams.py class
        # POSE ESTIMATION SETUP:
        self.poseEstimation = poseEstimation() # poseEstimation.py
        # PANDA3D SETUP:
        self.renderAR = renderAR(self) # renderAR.py class
        # RENDER LOOP:
        self.updateTask = self.taskMgr.add(self.renderLoop, 'renderLoop') # Task manager


    def renderLoop(self, task):
        # GET VIDEO FEED FRAME:
        self.cameraStreams.updateColorFrame(self) # cameraStreams.py
        # WORLD POSE UPDATE (Pose estimation):
        self.poseEstimation.update(self) # poseEstimation.py
        # UPDATE PANDA BACKGROUND VIDEO FEED:
        self.renderAR.updatePandaBackground(self) # renderAR.py
        # UPDATE PANDA CAMERA POSITION:
        self.renderAR.updateCamPos(self) # renderAR.py
        # RETURN LOOP:
        return task.cont


app = MainApp()
app.run()