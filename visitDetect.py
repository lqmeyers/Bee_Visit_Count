##trying to get number of visits from video 
#Luke Meyers 7/5/22

import numpy as np 
import h5py
import flowerFinder as ff 
import json
import math
from tabulate import tabulate

#filename = r"C:\Users\lqmey\Downloads\just_vid_7.analysis.h5.h"
filename = r"C:\Users\lqmey\Downloads\validation_22_22_6.analysis.h5.h"

def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst


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
    '''returns true if point inside rectangle defined by 4 corners.
    Uses y intercepts of lines parrelel to bounds intersecting coord 
    in qustion, and checks if in correct range. Bloated func becuase of all possible
    orders for coord entry '''
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
    rise2 = (y2-y3)
    run2 = (x2-x3)
    if rise1 != 0 and rise2 != 0 and run2 != 0 and run1 != 0: #for rotated rectangle
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
    
    else: #in off chance perfectly aligned with frame 
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
    for i in range(len(waistCoords)):
        if i == 0: #first frame 
          if insideRotRect(waistCoords[i],c1,c2,c3,c4) == True:
            iOut.append(i)
        elif i == len(waistCoords)-1: #last frame 
          if insideRotRect(waistCoords[i],c1,c2,c3,c4) == True:
            iOut.append(i)
        else: 
          if insideRotRect(waistCoords[i],c1,c2,c3,c4) == True and insideRotRect(waistCoords[i-1],c1,c2,c3,c4)==False:
            iOut.append(i)
          if insideRotRect(waistCoords[i],c1,c2,c3,c4) == False and insideRotRect(waistCoords[i-1],c1,c2,c3,c4)==True:
            iOut.append(i)
    return iOut


def getAllVisits(data,flower_config):
  '''gets all frame indicies where a bee is in the right spot'''
  all = [] 
  out = []
  for i in range(len(flower_config)):
    all.append([])
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:] 
    for f in range(len(flower_config)):
      found = detectVisit(justHead,makeCW(expandRect(flower_config[str(f)]['corners'],30)))
      #print('bee #',b,'at flower',f,'=',found)
      #print(np.array(found))
      if len(found) > 0:
        found = groupBy2(found,[b,f])#{'bee':b,'flower':f}) #groups into start and end frame sets
        all[f].append(found)
        #all= 1
  for i in all:
    out = out+i 
  return out 

def groupBy2(listIn,metadata):
  '''takes a list in and groups items into sets of 2 '''
  listOut = []
  for i in range(len(listIn))[0:len(listIn):2]:
    listOut.append([listIn[i],listIn[i+1],metadata])
  return (listOut)

  
def makeDict(listIn,mode='visits'):
  '''takes list output of cleanDetects and turns into dictionary 
  to prepare for writing to json'''
  dictOut = {}
  if mode == 'visits':
    for i in range(len(listIn)):
      dictOut[i] = {'start_frame':listIn[i][0],
                    'end_frame':listIn[i][1],
                    'track_id':listIn[i][2][0],
                    'flower_id':listIn[i][2][1]}
  else:
    dictOut= {'Visits_per_Flower':{},'Visits_per_Individual':{}}
    flowerList = range(len(listIn[0]))
    for i in flowerList:
      dictOut['Visits_per_Flower'][i] = listIn[0][i]
    
    for i in range(len(listIn[1])):
      dictOut['Visits_per_Individual'][i] = {}
      for f in flowerList:
        dictOut['Visits_per_Individual'][i][f] = listIn[1][i][f]
  return dictOut


def cleanDetects(listIn):
  '''Cleans list to get final indexes of visits. First filters detections to make 
  sure they last longer than 15 frames, then it checks list and makes sure visits are at least 5 
  frames apart, and if not, it combines them. Output as one long list of all recorded visits'''
  finals = [] #put finals here to get all visits appended together 
  for l in listIn:
    cleanD = []
    for de in l:
      if de[1] - de[0] > 15:
        cleanD.append(de) #only keeps visits longer than 5 frames 

    for i in range(len(cleanD)): #cleans through to make sure visits are seperate
      final = [] 
     
      if i == 0 and len(cleanD) > 1: #first visit in list, no previous 
        current = cleanD[i]
        next = cleanD[i+1]
        final.append(current[0])
        if next[0] < current[1]+5:
          final.append(next[1])
        else:
          final.append(current[1])
        final.append(current[2])

      elif i == (len(cleanD)-1) and len(cleanD)>1: #last visit in list, don't need to check after 
        current = cleanD[i]
        past = cleanD[i-1]
        if current[0] > past[1]+5:
          final.append(current[0])
          final.append(current[1])
        final.append(current[2])

      elif len(cleanD) == 1: #if only one visit for individual 
        current= cleanD[0]
        final.append(current[0]) 
        final.append(current[1])
        final.append(current[2])
      
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
        final.append(current[2])
      
      if len(final)>1: #clean empty detections
        finals.append(final)

  return finals 


def makeCW(corners):
    '''takes the corners that openCV generates and puts them in the 
    correct order for my logic functions'''
    cOut = []
    cOut.append(corners[3])
    cOut.append(corners[2])
    cOut.append(corners[1])
    cOut.append(corners[0])
    return cOut

def getStats(listIn,flowerConfig,tracks):
  '''makes a list with some relevant stats from cleanDetects
  before it is converted to dictionary''' 
  visitsPerFlower = np.zeros(shape=len(flowerConfig))
  visitsPerInd = np.zeros(shape=(len(tracks),len(flowerConfig)))
  for i in listIn:
    visitsPerFlower[i[2][1]] =  visitsPerFlower[i[2][1]] + 1 #tallies using val as index
    visitsPerInd[i[2][0]][i[2][1]] = visitsPerInd[i[2][0]][i[2][1]] + 1 
  return [visitsPerFlower,visitsPerInd]

##------------------where the magic happens----------------

#frameFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'
#ff.main(frameFile,2,show_validation=False)

#configFile = 'flower_patch_config.json'

def main(h5File,flowerConfigFile='flower_patch_config.json'):
  '''writes to a jvisits.son file all visit events given a h5 dataset and 
  config file of flower patch info'''
  tracks = parseTrackData(h5File)
  flower_config = json.load(open(flowerConfigFile))
  detects = getAllVisits(tracks,flower_config)
  cleans = cleanDetects(detects)
  statArray= getStats(cleans,flower_config,tracks)
  statistics = makeDict(statArray,'stats')
  results = makeDict(cleans)
  fullDict = {'Visits':results,'Statistics':statistics}
  with open('visits.json','w') as f:
    json.dump(fullDict,f,indent=3)
  return 

'''Ok so initialally I wrote everything to be done as a single function, main, above. However
when it came to displaying the data it became clear that a class would be necessary, even 
though I was largely unfamilier with them. Visits class runs all necessary track analysis upon 
initialization of the object, but various parts of the data can be accessed after the 
analysis pipeline is run. Additionally data can be displayed or saved in various formats '''

class visits:
  def __init__(self,file,flowerConfigFile='flower_patch_config.json'):
    self.file = file
    self.configFile = flowerConfigFile
    self.getTracks()
    self.getVisits()
    self.analyze()
    self.writeJSON()
  
  def getTracks(self):
    '''seperate tracks from h5'''
    self.tracks = parseTrackData(self.file)
  
  def getVisits(self):
    '''find all visit events from track data'''
    self.tracks = parseTrackData(self.file)
    self.patchConfig = json.load(open(self.configFile))
    detects = getAllVisits(self.tracks,self.patchConfig)
    self.visits = cleanDetects(detects)
    self.visitDict = makeDict(self.visits)
    self.total = len(self.visits)
    return(self.visits)
  
  def analyze(self):
    '''find some cumulative totals of visit events'''
    self.statArray = getStats(self.visits,self.patchConfig,self.tracks)
    self.statDict = makeDict(self.statArray,'stats')

  def writeJSON(self):
    '''write all visit info to visits.json'''
    fullDict = {'Visits':self.visitDict,'Statistics':self.statDict}
    with open('visits.json','w') as f:
      json.dump(fullDict,f,indent=3)

  ##add write to csv option!!!

  def displayPerInd(self):
    '''display table of total visits by individual'''
    listIn = np.ndarray.tolist(self.statArray[1])
    listIn.insert(0,['Track ID','Visits to Flower 0','Visits to Flower 1'])
    print(tabulate(listIn,headers='firstrow',tablefmt='fancy_grid',showindex=True))
  
  def displayPerFlower(self):
    '''display table of total visits by flower'''
    for v in range(len(self.statDict['Visits_per_Flower'])):
      self.statDict['Visits_per_Flower'][str(v)] = self.statDict['Visits_per_Flower'][str(v)]
      self.statDict['Visits_per_Flower']['Flower '+str(v)] = self.statDict['Visits_per_Flower'].pop(str(v))
    print(tabulate(self.statDict['Visits_per_Flower']))




#vs = visits(filename)
#vs.displayPerInd()
#print('ran')
