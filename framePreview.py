#code to be run only once 
import numpy as np 
import random 
import cv2 
import eventDetect as ed 
#from google.colab.patches import cv2_imshow

trackFile = r'C:\Users\lqmey\Downloads\fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5'
vidFile = r'C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\22_6_22_vids\fixed3x6_22_22_test.mp4'

#cap = cv2.VideoCapture('/content/fixed3x6_22_22_test.mp4')
cap = cv2.VideoCapture(vidFile)

tracks = ed.parseTrackData(trackFile)
tracks = np.moveaxis(tracks,0,1)

print(tracks.shape)
targetFrame = 320 ##could test switching this to decord for speed 

cap.set(1,targetFrame)
ret, img = cap.read()

scale = 65#downsize image for processing 
height = int(img.shape[0]*scale/100)
width = int(img.shape[1]*scale/100)
smaller = cv2.resize(img,(width,height))

detects = tracks[targetFrame]

for b in detects:
  color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
  for node in b:
    if np.any(np.isnan(node) == False):
      smaller = cv2.circle(smaller,(int(node[0]*scale/100),int(node[1]*scale/100)),3,color,-1) 

cv2_imshow(smaller)