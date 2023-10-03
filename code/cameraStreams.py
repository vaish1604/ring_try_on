# -*- coding: utf-8 -*-
import cv2 as cv

class cameraStreams:
    def __init__(self):
        self.lastColorFrame = None
        self.cap = cv.VideoCapture('D:\\Applications\\Try-on-panda3d\\data\\videoCapture\\hand1.mp4')
        
    def updateColorFrame(self, panda):
        success, img = self.cap.read()
        # print(success)
        if success:
            self.lastColorFrame = img
        else:
            # Loop video:
            print('End of video, looping')
            self.cap = cv.VideoCapture('D:\\panda\\data\\videoCapture\\handsss.mp4')
            success, img = self.cap.read()
            self.lastColorFrame = img

    def getColorFrame(self):
        return self.lastColorFrame

    # Used one time in renderAR.py init:
    def getColorImage(self):
        success, img = self.cap.read()
        return img
    
