# ring_try_on
This repo places a 3D ring on a hand 



      
## The modules and tasks in this project are:     
1. Hand Landmark detection:  Mediapipe
2. Pose estimation : custom function using rigid tranform
3. 3D modules are custom modules

## How to use:
Download your 3D models and place them in "data/model/" folder     
Then update the renderAR.py file    
```python
panda.banner = panda.loader.loadModel("../data/models/model_name.glb")
```
Select your desired video and upload it in the "data/videoCapture/" folder     
Update the cameraStreams.py file
```python
self.cap = cv.VideoCapture('../data/videoCapture/video_name.mp4')
```

Run the main.py file


https://github.com/vaish1604/ring_try_on/assets/80941602/aac56cd3-ef03-4f0b-a3c7-d8d62640c770

