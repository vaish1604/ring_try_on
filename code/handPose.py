# -*- coding: utf-8 -*-
import cv2 as cv
from panda3d.core import *
from panda3d.core import Mat3,Mat4
import mediapipe as mp
import numpy as np
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
from scipy.spatial.transform import Rotation as R

class poseEstimation:
    def __init__(self):
        # Pose estimation data: 
        self.c=0 #variable to make up update values for only 5 frames

        self.image_rows=0
        self.image_cols=0
        self.mp_hands = mp.solutions.hands

        self.flag=False
        self.A=None
        #rotation angles
        self.H=float(0) 
        self.P=float(0)
        self.R=float(0)
        #translation 
        self.camX=0
        self.camY=50
        self.camZ=0
    
    #function to get the 3D points of 6 landmarks
    def get_3d_data(self,results):
        
        # Loop through hands
        for hand in results.multi_hand_landmarks:
            data = [] 
            for i in [5,6,9,10,13,14]:
                data.append([hand.landmark[i].x, hand.landmark[i].y, hand.landmark[i].z])
            return np.array(data)

    #write utility function
    def rigid_transform_3D(self,A, B):
        assert A.shape == B.shape

        num_rows, num_cols = A.shape
        if num_rows != 3:
            raise Exception(f"matrix A is not 3xN, it is {num_rows}x{num_cols}")

        num_rows, num_cols = B.shape
        if num_rows != 3:
            raise Exception(f"matrix B is not 3xN, it is {num_rows}x{num_cols}")

        # find mean column wise
        centroid_A = np.mean(A, axis=1)
        centroid_B = np.mean(B, axis=1)

        # ensure centroids are 3x1
        centroid_A = centroid_A.reshape(-1, 1)
        centroid_B = centroid_B.reshape(-1, 1)

        # subtract mean
        Am = A - centroid_A
        Bm = B - centroid_B

        H = Am @ np.transpose(Bm)

        # sanity check
        #if linalg.matrix_rank(H) < 3:
        #    raise ValueError("rank of H = {}, expecting 3".format(linalg.matrix_rank(H)))

        # find rotation
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        # special reflection case
        if np.linalg.det(R) < 0:
            print("det(R) < R, reflection detected!, correcting for it ...")
            Vt[2,:] *= -1
            R = Vt.T @ U.T

        t = -R @ centroid_A + centroid_B

        return R, t
    
    #function to convert rotation matrix to euler 
    def get_rotation_vector(self,r):
        r= R.from_matrix(r)
        return r.as_euler('xyz', degrees=True)
    

    # POSE ESTIMATION METHOD:
    def update(self, panda):
        img = panda.cameraStreams.getColorFrame() # cameraStreams.py
        self.image_cols, self.image_rows, _ = img.shape
        #initializing hand landmark detection using mediapipe
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.3)
        
        results = hands.process(cv.cvtColor(img, cv.COLOR_BGR2RGB))

########ROTATION###############################################

        if results.multi_hand_landmarks:    
            if not self.flag:
                self.flag = True 
                self.A = self.get_3d_data(results)

            B = self.get_3d_data(results)
            r,_ = self.rigid_transform_3D(self.A.T, B.T)
        euler=self.get_rotation_vector(r)
########TRANSLATION###############################################
        #get landmark for middle finger point, stored at index 10 in landmark list
        if results.multi_hand_landmarks:
            for _, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    self.pos=hand_landmarks.landmark[mp_hands.HandLandmark(10).value]
            # TRANSLATION:
            # updating the translation values to place the ring at the desired position
        xTrans = int(self.pos.x*self.image_rows)
        zTrans = int(self.pos.y*self.image_cols)
        yTrans = int(self.pos.z*self.image_rows)

        #the coordinate systems are different, so we will convert the positions such that we shift (0,0) to the centre of the screen
        # and the corresponding translations are updates according 
        if(xTrans<(self.image_rows/2)):
            xTrans=-((self.image_rows/2)-xTrans)
        elif(xTrans>(self.image_rows/2)):
            xTrans=(xTrans-(self.image_rows/2))
        else:
            xTrans=0
        if(zTrans<(self.image_cols/2)):
            zTrans=-((self.image_cols/2)-zTrans)
        elif(zTrans>(self.image_cols/2)):
            zTrans=(zTrans-(self.image_cols/2))
        else:
            zTrans=0
        
        #now we will use variables to store the translation and rotation of the model
        # self.camX =  (xTrans*26)/(self.image_rows/2)
        # self.camY = yTrans
        # self.camZ = (zTrans*14)/(self.image_cols/2)
        #the values 26 and 14 were acquired by manually checking for the window of size (640,360) 

        if self.c%5==0: #we are calculating the rotation for every 5 frames to avoid high jittering in the project
            self.camX =  (xTrans*26)/(self.image_rows/2)
            self.camY = yTrans
            self.camZ = (zTrans*14)/(self.image_cols/2)
            self.H=euler[0]
            self.P=euler[2]
            self.R=euler[2]
        self.c+=1

        #finally storing the translation and rotation variables 
        panda.poseData['pandaCamPose']['trans'] = [self.camX, 50, -self.camZ] #the sign is put by trial-and-error 
        panda.poseData['pandaCamPose']['rot']   = [self.H-90, 90-self.P, 90+self.R] #the sign is put by trial-and-error
        
