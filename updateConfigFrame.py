##small script to update the frame read by flower finder 
#Luke Meyers 7/27/22

import cv2

vidFile = r"C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\22_6_22_vids\fixed2x6_22_22_test.mp4"
frameFile = r'C:\Users\lqmey\OneDrive\Desktop\Bee_Visit_Count\Images\targetFrame.tiff'

cap = cv2.VideoCapture(vidFile)
ret, frame = cap.read()
cv2.imwrite(frameFile,frame)

print('written')