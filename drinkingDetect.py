##trying to get number of visits from video 
#Luke Meyers 7/5/22


import timeit as ti
import numpy as np 
import h5py
import matplotlib.patches as ptch
import flowerFinder as ff 
import cv2


#filename = r"C:\Users\lqmey\Downloads\just_vid_7.analysis.h5.h"
filename = r"C:\Users\lqmey\Downloads\validation_22_22_6.analysis.h5.h"


with h5py.File(filename,'r') as f:
  dset_names = list(f.keys())
  locations = f['tracks'][:].T
  node_names = [n.decode() for n in f['node_names'][:]]


#""" #some info about the h5 dataset 
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

setup = """
import matplotlib.patches as ptch
"""
#myBox="""
def insideBox(coords,center):
  '''returns true if inside, returns false if not'''
  #center = [1380,480]
  bound = 50 
  allcoords = []
  x = coords[0] 
  y = coords[1]
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
#"""
#my_code = """ 
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

#print(insideCircle([50,50],[0,0]))


#"""
#print('time for insidecircle to run',ti.timeit(setup=setup,stmt=my_code,number=100000))
#print('Time for insidebox to run',ti.timeit(setup=setup,stmt=myBox,number=100000))


def detectHead(headCoords,center,mode='box'):
    '''takes a list of head coords and returns the indexes of frames 
    where they are inside the bounding box'''
    iOut = []
    cOut = [] 
    #circ = ptch.Circle((center),radius = 50)
    #circ = ptch.Rectangle((center[0]-50,center[1]-50),100,100)
    for i in range(len(headCoords)):
      if mode == 'box':
        #'''   #decided to first get all frames with detection instead of filtering unnecesarily on non-detected frames 
        if insideBox(headCoords[i],center) == True and insideBox(headCoords[i-1],center)==False:
            iOut.append(i)
        elif insideBox(headCoords[i],center) == False and insideBox(headCoords[i-1],center)==True:
            iOut.append(i)
        #print(i,'heads detected inside box')
      #'''
      elif mode == 'circle':
        if insideCircle(headCoords[i],center) == True and insideCircle(headCoords[i-1],center)==False:
            iOut.append(i)
        elif insideCircle(headCoords[i],center) == False and insideCircle(headCoords[i-1],center)==True:
            iOut.append(i)
        #print('frame #'i,'heads detected inside circle')
      else:
        print('unaccepted mode!')
        break
    print(iOut)
    return iOut#,cOut 


'''ok so parameters of a drinking visit: 
longer than 15 frames, seperated by at least 5 frames from other visits '''

#print(trackFirst[1].shape)

def getAll(data,center1,center2):
  '''gets all frame indicies where a bee is in the right spot'''
  allWhite = [] 
  allBlue = []
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:] 
    #found = detectHead(justHead,center1)
    #print('flower1 box bee #',b)
    found = detectHead(justHead,center1,'circle')
    #print('flower1 circle bee #',b)
    if len(found) > 0:
      allWhite.append(found)
    #found = detectHead(justHead,center2)
    #print('flower2 box bee #',b)
    found = detectHead(justHead,center2,'circle')
    #print('flower2 circle bee #',b)
    if len(found) > 0:
      allBlue.append(found)
  return allWhite+allBlue


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
  sure they last longer than 5 frames, then it checks list and makes sure visits are at least 5 
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
        
      
##------------------where the magic happens----------------
#whiteFlower =  [1380,480] #use these for file 5
#blueFlower = [630,550]

frameFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'

whiteCenter = ff.main(frameFile,'center',show_validation=True)[0]
blueCenter = ff.main(frameFile,'center',show_validation=True)[1]


trackFirst = np.moveaxis(locations,-1,0)
#trackSecond = np.moveaxis(locations,-1,1)

whiteFlower = [535,675]
blueFlower = [1345,595]
detects = getAll(trackFirst,whiteFlower,blueFlower)
#detects = getAll(trackFirst,whiteCenter,blueCenter)
cleanDetect = cleanDetects(detects)
print(len(cleanDetect))
#print(cleanDetect)
print('ran')

'''
#some data exploration 
print(trackSecond.shape)
for i in range(len(trackSecond[:,0,0,0])):
  print(i)
  print(trackSecond[i,:,3,:])
  '''