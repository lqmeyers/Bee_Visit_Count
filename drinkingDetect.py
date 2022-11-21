##trying to get number of visits from video 
#Luke Meyers 7/5/22


import timeit as ti
import numpy as np 
import h5py
import matplotlib.patches as ptch
import flowerFinder as ff 
import cv2
import json
import csv
from tabulate import tabulate
import datetime


#filename = r"C:\Users\lqmey\Downloads\just_vid_7.analysis.h5.h"
#filename = r"C:\Users\lqmey\Downloads\validation_22_22_6.analysis.h5.h"
#filename = r'/home/lqmeyers/SLEAP_files/h5_files/fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5'


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

#trackFirst = np.moveaxis(locations,-1,0) #move axis I think will do the trick 
#print(trackFirst[0])

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
    #print(iOut)
    return iOut#,cOut 


'''ok so parameters of a drinking visit: 
longer than 15 frames, seperated by at least 5 frames from other visits '''

#print(trackFirst[1].shape)



def getAll(data,flower_config):
  '''gets all frame indicies where a bee is in the right spot'''
  all = [] 
  out = []
  for i in range(len(flower_config)):
    all.append([])
  for b in range(len(data)):
    justHead = data[b]
    justHead = justHead[:,3,:] 
    for f in range(len(flower_config)):
      found = detectHead(justHead,(flower_config[str(f)]['center']),'circle')
      #print(b,' ',found)
      #print('bee #',b,'at flower',f,'=',found)
      #print(np.array(found))
      if len(found) > 0:
        found = groupBy2(found,[b,f])#{'bee':b,'flower':f}) #groups into start and end frame sets
        #print(found)
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

  
#testL = [1,2,3,4,5,6]
#print(groupBy2(testL))
  

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

 
def makeDict(listIn,mode='drinking'):
  '''takes list output of cleanDetects and turns into dictionary 
  to prepare for writing to json'''
  dictOut = {}
  if mode == 'drinking':
    for i in range(len(listIn)):
      dictOut[i] = {'start_frame':listIn[i][0],
                    'end_frame':listIn[i][1],
                    'track_id':listIn[i][2][0],
                    'flower_id':listIn[i][2][1]}
  else:
    dictOut= {'Drinks_per_Flower':{},'Drinks_per_Individual':{}}
    flowerList = range(len(listIn[0]))
    for i in flowerList:
      dictOut['Drinks_per_Flower'][i] = listIn[0][i]
    
    for i in range(len(listIn[1])):
      dictOut['Drinks_per_Individual'][i] = {}
      for f in flowerList:
        dictOut['Drinks_per_Individual'][i][f] = listIn[1][i][f]
  return dictOut       

def getStats(listIn,flowerConfig,tracks):
  '''makes a list with some relevant stats from cleanDetects
  before it is converted to dictionary''' 
  drinksPerFlower = np.zeros(shape=len(flowerConfig))
  drinksPerInd = np.zeros(shape=(len(tracks),len(flowerConfig)))
  for i in listIn:
    drinksPerFlower[i[2][1]] =  drinksPerFlower[i[2][1]] + 1 #tallies using val as index
    drinksPerInd[i[2][0]][i[2][1]] = drinksPerInd[i[2][0]][i[2][1]] + 1 
  return [drinksPerFlower,drinksPerInd]

##------------------where the magic happens----------------

class drinks:
  def __init__(self,file,vidFile,flowerConfigFile='flower_patch_config.json'):
    self.file = file
    self.vidFile = vidFile
    self.configFile = flowerConfigFile
    self.getTracks()
    self.getDrinks()
    self.analyze()
    self.writeJSON()
    self.writeCSV()
  
  def getTracks(self):
    '''seperate tracks from h5'''
    self.tracks = parseTrackData(self.file)
   
  
  def getDrinks(self):
    '''find all visit events from track data'''
    self.tracks = parseTrackData(self.file)
    self.patchConfig = json.load(open(self.configFile))
    detects = getAll(self.tracks,self.patchConfig)
    self.drinks = cleanDetects(detects)
    self.drinkDict = makeDict(self.drinks)
    self.total = len(self.drinks)
    return(self.drinks)
  
  def analyze(self):
    '''find some cumulative totals of visit events'''
    self.statArray = getStats(self.drinks,self.patchConfig,self.tracks)
    self.statDict = makeDict(self.statArray,'stats')

  def writeJSON(self):
    '''write all visit info to drinks.json'''
    fullDict = {'Init':{'VidFile':self.vidFile,'Datetime':str(datetime.datetime.now())},'Drinking_Events':self.drinkDict,'Statistics':self.statDict}
    with open('drinks.json','w') as f:
      json.dump(fullDict,f,indent=3)

  def writeCSV(self):
    '''writes all drinking events to drinks.csv'''
    listIn = []
    for key in range(len(self.drinkDict)):
      self.drinkDict[key]['event_num']=key #moving index inside dict 
      listIn.append(self.drinkDict[key])
    keyList = [] 
    for l in listIn[0].keys():
      keyList.append(l)
    with open('drinks.csv','w') as f:
      writer = csv.DictWriter(f,fieldnames=keyList)
      writer.writeheader()
      writer.writerows(listIn)

  def displayPerInd(self):
    '''display table of total drinks by individual'''
    listIn = np.ndarray.tolist(self.statArray[1])
    listIn.insert(0,['Track ID','Drinking Events at Flower 0','Drinking Events at Flower 1'])
    print(tabulate(listIn,headers='firstrow',tablefmt='fancy_grid',showindex=True))
  
  def displayPerFlower(self):
    '''display table of total drinks by flower'''
    flowerDict = self.statDict['Drinks_per_Flower']
    for v in range(len(flowerDict)):
      flowerDict[v] = [flowerDict[v]]
      flowerDict['Flower '+str(v)] = flowerDict.pop(v)
    print(tabulate(flowerDict,headers='keys',tablefmt='fancy_grid'))

#vid = "/mnt/c/Users/lqmey/OneDrive/Desktop/fixed2x6_22_22_test.mp4"
#filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h"
#d = drinks(filename,vid)
#d.displayPerFlower()
#print('found')