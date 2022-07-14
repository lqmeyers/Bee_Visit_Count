##Program to find coordinates of 2 artificial flowers in flower patch expiraments
#Luke Meyers 7/11/22


import numpy as np 
import cv2

#vidFile = r"C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\20_6_22_vids\fixed2x6_20_22_test.mp4"
imgFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'

def main(file,mode='center',show_validation=True):
    '''recieves image file and finds flower coords. If mode = center
    returns center coords, else corners. If show validation = True will plot
    and display results on image'''
    img = cv2.imread(imgFile)

    scale = 50 #downsize image for processing 
    height = int(img.shape[0]*scale/100)
    width = int(img.shape[1]*scale/100)
    smaller = cv2.resize(img,(width,height))

    b, g, r = cv2.split(smaller) #split into color channels 

    blur = cv2.medianBlur(b,5) #begin working with only blue channel

    thresh = cv2.threshold(blur,25,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1] #binary threshold

    contours, hier = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        # Fill smallest contours with zero (erase small contours).
        if area < 300:
            cv2.fillPoly(thresh, pts=[c], color=0)
            continue

    contours, hier = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    bl = (boxList(contours))
    bl.sort(key=lambda x: np.average(x[1]),reverse=True) #sorts by largest 

    whiteFlower = bl[0] #takes just two largest rectangles
    blueFlower = bl[1]
    if np.average(whiteFlower[1]) < 150 or np.average(blueFlower[1]) < 150  : 
        return "POTENTIAL ERROR: FLOWER BOUNDS SMALLER THAN EXPECTED"

    whiteCenter = whiteFlower[0] #pulls out center coord
    blueCenter = blueFlower[0]

    #print(whiteCenter)
    #print(blueCenter)
    unscale = (1/(scale/100))
   
    whiteCenter = (int(whiteCenter[0]*unscale),int(whiteCenter[1]*unscale))
    blueCenter = (int(blueCenter[0]*unscale),int(blueCenter[1]*unscale))

    whiteCoords = getCorners(whiteFlower)
    blueCoords = getCorners(blueFlower)
    
    tckr = 0 
    for p in whiteCoords:
        whiteCoords[tckr] = [int(p[0]*unscale),int(p[1]*unscale)]
        tckr = tckr + 1
    tckr = 0    
    for p in blueCoords:
        blueCoords[tckr] = [int(p[0])*unscale,int(p[1]*unscale)]
        tckr = tckr+1


    if show_validation == True:
        if mode == 'center':
            img = cv2.circle(img,whiteCenter,4, (0,0,255), -1)
            img = cv2.circle(img,blueCenter,4, (0,0,255), -1)
        else:
            for p in whiteCoords:
                img = cv2.circle(img,p,4, (0,255,255), -1)
            for p in blueCoords:
                img = cv2.circle(img,p,4, (0,255,255), -1)
        cv2.imshow('display',img)
        cv2.waitKey()

    if mode == 'center':
        print(whiteCenter,blueCenter)
        return([whiteCenter,blueCenter])
    else: 
        print(whiteCoords,blueCoords)
        return([whiteCoords,blueCoords])
    

def boxList(contours):
    '''fits a rectangle to all contours and returns list of 
    cv rotated rect = [center,hw,angle]'''
    out = [] 
    for c in contours:
        box = cv2.minAreaRect(c)
        boxL = list(box)
        #print(boxL)
        out.append(boxL)
        #print('next')
        #rect = cv2.drawContours(smaller,[box],0,(0,0,255,2))
    return(out)


def getCorners(rotRect):
    '''returns the corners of a rotated rect + center'''
    box = cv2.boxPoints(rotRect)
    return(np.int0(box))
#print(box)


#main(imgFile,'corners')
#print('ran')
