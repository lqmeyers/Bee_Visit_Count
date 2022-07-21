##trying to get number of visits from video 
#Luke Meyers 7/5/22


import timeit as ti
import numpy as np 
import h5py
import matplotlib.patches as ptch
import flowerFinder as ff 
import cv2
import json
import math


#filename = r"C:\Users\lqmey\Downloads\just_vid_7.analysis.h5.h"
filename = r"C:\Users\lqmey\Downloads\validation_22_22_6.analysis.h5.h"


with h5py.File(filename,'r') as f:
  dset_names = list(f.keys())
  locations = f['tracks'][:].T
  node_names = [n.decode() for n in f['node_names'][:]]


""" #some info about the h5 dataset 
print('-----------filename---------------')
print(filename)
print()

print('-----------HDF5 datasets----------')
print(dset_names)
print()

print('-----------locations datashape---------')
print(locations.shape)
print()
frame_count, node_count, _, instance_count = locations.shape
print('frame count:', frame_count)
print('node count:', node_count)
print('instance count', instance_count)
print()

print('----------nodes----------')
for i, name in enumerate(node_names):
  print(f'{i}: {name}')
  print()
#"""

trackFirst = np.moveaxis(locations,-1,0) #move axis I think will do the trick 
#print(trackFirst[0])


def insideBox(coord,center,bound=50):
  '''returns true if inside square at center, returns false if not'''
  #center = [1380,480]
  #= 50 
  allcoords = []
  x = coord[0] 
  y = coord[1]
  if x >= center[0]-bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if x <= center[0]+bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y >= center[1]-bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y <= center[1]+bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if False in allcoords:
    return False
  else: 
    return True 

def insideCircle(coords,center):
  '''returns true if coords inside circle at center, false if not'''
  bound = 50
  xIn = coords[0]
  yIn = coords[1]
  xC = center[0]
  yC = center[1]
  if ((xIn-xC)**2) + ((yIn-yC)**2) <= bound**2:
    return True 
  else:
    return False 

def insideRotRect(coord,corner1,corner2,corner3,corner4):
    '''returns true if point inside rectangle defined by 4 corners'''
    x1 = corner1[0]
    y1 = corner1[1]
    x2 = corner2[0]
    y2 = corner2[1]
    x3 = corner3[0]
    y3 = corner3[1]
    x4 = corner4[0]
    y4 = corner4[1]
    xC = coord[0]
    yC = coord[1]
    rise1 = (y1-y2)
    run1 = (x1-x2)
    #print('m1=',m1)
    rise2 = (y2-y3)
    run2 = (x2-x3)
    if rise1 != 0 and rise2 != 0 and run2 != 0 and run1 != 0:
        m1 = rise1/run1
        m2 = rise2/run2
        #print('m2=',m2)
        b1 = y1-(m1*x1)
        #print('b1=',b1)
        b2 = y4-(m1*x4)
        #print('b2=',b2)
        b3 = y1-(m2*x1)
        #print('b3=',b3)
        b4 = y2-(m2*x2)
        #print('b4=',b4)
        bC1 = yC-(m1*xC)
        #print('b? with slope 1=',bC1)
        bC2 = yC-(m2*xC)
        #print('b? with slope 2=',bC2)
        if b4>=b3 and b1 >=b2: #case1 
            if bC1 < b1 and bC1 > b2 and bC2 > b3 and bC2 < b4:
                return True 
            else:
                return False
        elif b4<=b3 and b1 >=b2: #case2
            if bC1 < b1 and bC1 > b2 and bC2 < b3 and bC2 > b4:
                return True 
            else:
                return False
        elif b4>=b3 and b1<=b2: #case3
            if bC1 > b1 and bC1 < b2 and bC2 > b3 and bC2 < b4:
                return True 
            else:
                return False
        elif b4<=b3 and b1<=b2: #case4 
            if bC1 > b1 and bC1 < b2 and bC2 < b3 and bC2 > b4:
                return True 
            else:
                return False
        else:
            print('coords not in sequential order!')
            #break
    else:
        if x1 < x2 and y2 > y3:
            centerX = ((x2-x1)/2)+x1
            centerY = ((y2-y3)/2)+y3
            bound = (x2-x1)/2
        elif x4 < x1 and y1 > y2:
            centerX = ((x1-x4)/2)+x4
            centerY = ((y1-y2)/2)+y2
            bound = (x1-x4)/2
        elif x3 < x4 and y4 > y1:
            centerX = ((x4-x3)/2)+x3
            centerY = ((y4-y1)/2)+y1
            bound = (x4-x3)/2
        elif x2 < x3 and y3 > y4:
            centerX = ((x3-x2)/2)+x1
            centerY = ((y3-y4)/2)+y4
            bound = (x3-x2)/2
        if insideBox((xC,yC),(centerX,centerY),bound) == True:
            return True 
        else:
            return False 
    

#c1 = (6,1)
#c2 = (1,1)
#c3 = (1,6)
#c4 = (6,6)
#cInq = (0,3)
#print(insideRotRect(cInq,c1,c2,c3,c4))

#print(insideCircle([50,50],[0,0]))

#"""
#print('time for insidecircle to run',ti.timeit(setup=setup,stmt=my_code,number=100000))
#print('Time for insidebox to run',ti.timeit(setup=setup,stmt=myBox,number=100000))

def expandRect(coordsIn,buffer):
    '''expands a rectangle buffer distance from each side
    when given corner coordinates given as a list'''
    c1 = coordsIn[0]
    c2 = coordsIn[1]
    c3 = coordsIn[2]
    c4 = coordsIn[3]
    rise = abs(c4[1]-c3[1])
    run = abs(c4[0]- c3[0])
    #print(rise,run)
    theta = 2.356 - math.atan(rise/run)
    short = abs(buffer*math.sin(theta))
    long = abs(buffer*math.cos(theta))
    c1 = [c1[0]-long,c1[1]+short]
    c2 = [c2[0]+long,c2[1]+short]
    c3 = [c3[0]+short,c3[1]-long]
    c4 = [c4[0]-long,c4[1]-short]
    return [c1,c2,c3,c4]


def detectVisit(waistCoords,corners):
    '''takes a list of waist coords and returns the indexes of frames 
    where they are inside box defined by corners, usually flower borders'''
    iOut = []
    c1 = corners[0]
    c2 = corners[1]
    c3 = corners[2]
    c4 = corners[3]
    #circ = ptch.Circle((center),radius = 50)
    #circ = ptch.Rectangle((center[0]-50,center[1]-50),100,100)
    for i in range(len(waistCoords)):
        if insideRotRect(waistCoords[i],c1,c2,c3,c4) == True and insideRotRect(waistCoords[i-1],c1,c2,c3,c4)==False:
            iOut.append(i)
        if insideRotRect(waistCoords[i],c1,c2,c3,c4) == False and insideRotRect(waistCoords[i-1],c1,c2,c3,c4)==True:
            iOut.append(i)
    #print(iOut)
    return iOut#,cOut 


def getAllVisits(data,flower_config):
  '''gets all frame indicies where a bee is in the right spot'''
  all = [] 
  out = []
  for i in range(len(flower_config)):
    all.append([])
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:]  #this is actually still head lol 
    for f in range(len(flower_config)):
      found = detectVisit(justHead,makeCW(expandRect(flower_config[str(f)]['corners'],30)))
      if len(found) > 0:
        all[f].append(found)
        #all= 1
  for i in all:
    out = out+i 
  return out 

'''
test = np.zeros(shape=(5,2))
test[2] = [3,4]
test[3]= [nan,nan]
cTest = test[~np.isnan(test)]
print(cTest)
'''
#print('Time for DetectHead with Circles to run',ti.timeit(setup=setup,stmt=my_Circle,number=100000))
#print('Time for DetectHead with Circles to run',ti.timeit(setup=setup,stmt=my_Circle,number=100000))
#print(detects)

def groupBy2(listIn):
  '''takes a list in and groups items into sets of 2 '''
  listOut = []
  for i in range(len(listIn))[0:len(listIn):2]:
    listOut.append([listIn[i],listIn[i+1]])
  return listOut
    
#testL = [1,2,3,4,5,6]
#print(groupBy2(testL))
  

def cleanDetects(listIn):
  '''Cleans list to get final indexes of visits. First filters detections to make 
  sure they last longer than 15 frames, then it checks list and makes sure visits are at least 5 
  frames apart, and if not, it combines them. Output as one long list of all recorded visits'''
  cleanV = []
  finals = [] #put finals here to get all visits appended together 
  for l in listIn:
    d = groupBy2(l) #groups into start and end frame sets
    cleanD = []
    for de in d:
      if de[1] - de[0] > 15:
        cleanD.append(de) #only keeps visits longer than 5 frames 
    #print(cleanD)
     #finals = [] #put it here to keep visits grouped by track/individual 
    for i in range(len(cleanD)): #cleans through to make sure visits are seperate
      final = [] 
      #print(i)
      if i == 0 and len(cleanD) > 1: #first visit in list, no previous 
        current = cleanD[i]
        next = cleanD[i+1]
        final.append(current[0])
        if next[0] < current[1]+5:
          final.append(next[1])
        else:
          final.append(current[1])
      elif i == (len(cleanD)-1) and len(cleanD)>1: #last visit in list, don't need to check after 
        current = cleanD[i]
        past = cleanD[i-1]
        if current[0] > past[1]+5:
          final.append(current[0])
          final.append(current[1])
      elif len(cleanD) == 1: #if only one visit for individual 
        current= cleanD[0]
        final.append(current[0]) #do it seperately to not get another set of brackets 
        final.append(current[1])
      else: #other visits, in the middle of a set 
        next = cleanD[i+1]
        current = cleanD[i]
        past = cleanD[i-1]
        if current[0] > past[1]+5:
          final.append(current[0])
          if next[0] < current[1]+5:
            final.append(next[1])
          else:
            final.append(current[1])
      if len(final)>0: #clean empty detections
        finals.append(final)
    #if len(finals) > 0: #uncomment this if grouping by individual 
      #cleanV.appenf(finals)
  return finals #return finals if getting all visits together
  #return cleanV

def makeCW(corners):
    '''takes the corners that openCV generates and puts them in the 
    correct order for my logic functions'''
    cOut = []
    cOut.append(corners[3])
    cOut.append(corners[2])
    cOut.append(corners[1])
    cOut.append(corners[0])
    return cOut
      
##------------------where the magic happens----------------

frameFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'
ff.main(frameFile,2,show_validation=False)

configFile = 'flower_patch_config.json'
f = open(configFile)
flower_config = json.load(f)


detects = getAllVisits(trackFirst,flower_config)
cleanDetect = cleanDetects(detects)
print(len(cleanDetect))

print('ran')


'''
#some data exploration 
print(trackSecond.shape)
for i in range(len(trackSecond[:,0,0,0])):
  print(i)
  print(trackSecond[i,:,3,:])

'''