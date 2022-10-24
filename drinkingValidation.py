##trying to get number of visits from video 
#Luke Meyers 7/5/22



import numpy as np 
import h5py
import matplotlib as mpl 
from matplotlib import pyplot as plt


filename = r"C:\Users\lqmey\Downloads\validation_22_22_6.analysis.h5.h"
#filename = r"C:\Users\lqmey\Downloads\validation_22_20_6.analysis.h5 (1).h"

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
'''
justHead = trackFirst[0]
justHead = justHead[:,0,:] #take just the first of the second set 
#print(justHead) #this gives a list of all the head coordinates 
'''
def insideBox(coords,center):
  '''returns true if inside, returns false if not'''
  #center = [1380,480]
  bound = 50
  allcoords = [] 
  if coords[0] >= center[0]-bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if coords[0] <= center[0]+bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if coords[1] >= center[1]-bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if coords[1] <= center[1]+bound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if False in allcoords:
    return False
  else: 
    return True 

def detectHead(headCoords,center):
    '''takes a list of head coords and returns the indexes of frames 
    where they are inside the bounding box'''
    iOut = []
    cOut = [] 
    for i in range(len(headCoords)):
      #'''   #decided to first get all frames with detection instead of filtering unnecesarily on non-detected frames 
        if insideBox(headCoords[i],center) == True and insideBox(headCoords[i-1],center)==False:
            iOut.append(i)
        elif insideBox(headCoords[i],center) == False and insideBox(headCoords[i-1],center)==True:
            iOut.append(i)
      #'''
    return iOut#,cOut 

'''ok so parameters of a drinking visit: 
longer than 5 frames, seperated by at least 5 frames from other visits '''


#print(trackFirst[1].shape)

def getAll(data,center1,center2):
  '''gets all frame indicies where a bee is in the right spot'''
  all = [] 
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:]
    found = detectHead(justHead,center1)
    if len(found) > 0:
      all.append(found)
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:]
    found = detectHead(justHead,center2)
    if len(found) > 0:
      all.append(found)
  return all 

#hu = [] 
#print(len(hu))

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
whiteFlower =  [535,675] #use these for 6/22 file
#whiteFlower =   [1380,500] #there for 6/20
blueFlower = [1345,595]
#blueFlower = [640,530]
trackFirst = np.moveaxis(locations,-1,0)
detects = getAll(trackFirst,whiteFlower,blueFlower)
print(len(cleanDetects(detects)))
#print(cleanDetects(detects))
print('ran')
