##Program to find coordinates of 2 artificial flowers in flower patch expiraments
#Luke Meyers 7/11/22


from re import S
import numpy as np 
import cv2
import json
import datetime
import math 

#vidFile = r"C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\20_6_22_vids\fixed2x6_20_22_test.mp4"
#imgFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'
#imgFile = r'C:\Users\lqmey\OneDrive\Desktop\Bee_Visit_Count\Images\targetFrame.tiff'


def main(vid,flowerNum,show_validation=True,run_on_colab=False):
    '''recieves vid file and finds coords of flowerNum # of flowers. If mode = center
    returns center coords, else corners. If show validation = True will plot
    and display results on image'''
    vidName = getName(vid)

    cap = cv2.VideoCapture(vid)
    ret, frame = cap.read()
    cv2.imwrite("./Images/targetFrame.tiff",frame)
    print('written')

    img = cv2.imread("./Images/targetFrame.tiff")

    #img = frame 
    scale = 50 #downsize image for processing 
    height = int(img.shape[0]*scale/100)
    width = int(img.shape[1]*scale/100)
    smaller = cv2.resize(img,(width,height))

    b, g, r = cv2.split(smaller) #split into color channels 

    blur = cv2.medianBlur(b,5) #begin working with only blue channel

    thresh = cv2.threshold(blur,25,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1] #binary threshold

    contours, hier = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)[-2:]
    for c in contours:
        area = cv2.contourArea(c)
        # Fill smallest contours with zero (erase small contours).
        if area < 300:
            cv2.fillPoly(thresh, pts=[c], color=0)
            continue

    contours, _ = cv2.findContours(thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)[-2:]
    bl = (boxList(contours))
    bl.sort(key=lambda x: np.average(x[1]),reverse=True) #sorts by largest 

    flowerList = []
    flowerDict = {}
   
    for n in range(flowerNum):
       flowerList.append(bl[n])

    #whiteFlower = bl[0] #takes just two largest rectangles
    # blueFlower = bl[1]
    unscale = (1/(scale/100))

    tckr = 0 
    for f in flowerList:
        if np.average(f[1]) < 150:
            #return "POTENTIAL ERROR: FLOWER BOUNDS SMALLER THAN EXPECTED"
            hi=0 #placeholder
        else:
            flowerCenter = f[0]
            flowerCorners = getCorners(f)
            flowerCorners = flowerCorners.tolist()
            smaller = cv2.circle(smaller,(int(flowerCenter[0]),int(flowerCenter[1])),4,(0,0,255),-1) #flowerDict[f]['center']
            t = 0 
            for p in flowerCorners:
                flowerCorners[t] = [int(p[0]*unscale),int(p[1]*unscale)]
                t = t + 1
            flowerDict[tckr]={'center':(int(flowerCenter[0]*unscale),int(flowerCenter[1]*unscale)),
                            'corners':flowerCorners,'length':(pythagMe(flowerCorners[0],flowerCorners[1]),pythagMe(flowerCorners[1],flowerCorners[2]))}
        tckr = tckr+1
    if show_validation == True:
        #img = cv2.circle(img,whiteCenter,4, (0,0,255), -1)
        #img = cv2.circle(img,blueCenter,4, (0,0,255), -1)
        for f in range(len(flowerDict)):
            for p in flowerDict[f]['corners']:
                smaller = cv2.circle(smaller,(int(p[0]/unscale),int(p[1]/unscale)),4, (0,255,255), -1)
        if run_on_colab == False:
            cv2.imshow('display',smaller)
            cv2.setWindowProperty('display',cv2.WND_PROP_TOPMOST,1)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
        elif run_on_colab == True:
            from google.colab.patches import cv2_imshow
            cv2_imshow(smaller)

        #cv2.destroyAllWindows()
    flowerDict['Init']={'Video_Name':vidName,'Datetime':str(datetime.datetime.now())}
    with open('flower_patch_config.json','w') as f:
        json.dump(flowerDict,f,indent=3)
    return
 
def pythagMe(coord1,coord2):
    '''performs pythagorean theorum to return the
    distance between two points. Input coords as [x,y]'''
    x1 = coord1[0]
    y1 = coord1[1]
    x2 = coord2[0]
    y2 = coord2[1]
    return math.sqrt((y2-y1)**2+(x2-x1)**2)

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

def getName(file):
    '''uses a path string to get the name of a file'''
    strOut = ''
    i = 1
    while file[-i] != '/':
        i = i + 1
        #print(file[-i])
    strOut = file[-i:]
    return strOut


#vidFile = r"/home/lqmeyers/SLEAP_files/Bee_vids/22_6_22_vids/fixed2x6_22_22_test.mp4"
#results = main(vidFile,2,show_validation=False)
#json_string = json.dumps(results,indent=3)
#print(json_string)

#print('filename is '+getName(vidFile))
#print('ran')
