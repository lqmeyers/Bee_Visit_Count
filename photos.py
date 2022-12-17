## a complete script for extracting all the photos from a video


import cv2 
import h5py 
import datetime
import numpy as np
import math
import sys 
import json
import random
from matplotlib import pyplot as plt 

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

import profilePic as pp 
#import flowerFinder as ff
#import visitDetect as vd 
#import drinkingDetect as dd 


##funcs used for data handling (eventually will be made into utils.py)

def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst

def parseTrackScores(file,mode='instance'):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    dset_names = list(f.keys())
    #print(dset_names)
    if mode == 'instance':
      scores = f['instance_scores'][:].T
    else:
      scores = f['tracking_scores'][:].T
  return scores


def insideRect(coords,center,w,h):
  '''returns true if inside, returns false if not'''
  #center = [1380,480]
  xBound = w/2
  yBound = h/2
  allcoords = []
  x = coords[0] 
  y = coords[1]
  if x >= center[0]-xBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if x <= center[0]+xBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y >= center[1]-yBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y <= center[1]+yBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if False in allcoords:
    return False
  else: 
    return True 

def coordDist(coord1,coord2):
  '''computes the distance between two coordinates inputed as tuples'''
  x1 = coord1[0]
  y1 = coord1[1]
  x2 = coord2[0]
  y2 = coord2[1]
  a = abs(x2-x1)
  b = abs(y2-y1)
  c = math.sqrt((a**2)+(b**2))
  return abs(c)

  
def getName(file):
    '''uses a path string to get the name of a file'''
    strOut = ''
    i = 1
    while file[-i] != '/':
        i = i + 1
        #print(file[-i])
    strOut = file[-i:]
    return strOut

##---------------photo class----------------------------------


class photoSet:
    def __init__(self,trackFile,vidFile):
        self.trackFile = trackFile 
        self.vidFile = vidFile
        self.tracks = self.getTracks()
        self.instScores = self.getScores()
        self.trackScores = self.getScores('tracks')
        self.cleanliness(True)
        self.setScoreLimits(.99,.2)
        self.setNumPerTrack(6)
        self.setOutPath()
        self.jsonName = (str(self.outPath+getName(self.vidFile)[1:]+(datetime.datetime.now().strftime('.%d.%m.%Y.%H.%M.%S.')+'photolog.json')))
        self.photoDict = {}
       

    def getTracks(self):
        '''seperate tracks from h5'''
        self.tracks = parseTrackData(self.trackFile)
        return self.tracks
    
    def getScores(self,mode='instance'):
        '''seperates scores from h5'''
        self.scores = parseTrackScores(self.trackFile,mode)
        return self.scores

    def setScoreLimits(self,instanceScore,trackScore):
        '''inits score threshold for saving photos'''
        self.minInstScore = instanceScore
        self.minTrackScore = trackScore
    
    def setInterval(self,interval):
        '''determines frame interval between repeat captures'''
        self.interval = interval

    def setNumPerTrack(self,num):
        '''set number of repeat imgs per track'''
        self.numPerTrack = num
        self.limitNum = True

    def setOutPath(self,path='/home/lqmeyers/SLEAP_files/Bee_imgs/'):
        '''sets outpath for writing images, if you need to specify'''
        self.outPath = path

    def cleanliness(self,mode):
        '''determines if other bees are allowed in frame'''
        self.cleanliness = mode

    def getFrames(self,id):
        '''scans through all frames of an np array and returns a list of ones worth saving as a dictionary item with the
        track id'''
        approvedFrames = [] 
        for f in range(len(self.tracks[id])):
            if self.trackScores[f][id] > self.minTrackScore and self.instScores[f][id]  > self.minInstScore:
                approvedFrames.append(f)
        if self.cleanliness == True:
            trackLast = np.moveaxis(self.tracks,0,-1)
            tracks = np.moveaxis(trackLast,-1,2) #change shape from format expectec in most other functions 
            all = [] 
            for f  in range(len(approvedFrames)):
                bCheck = []
                bees = tracks[approvedFrames[f]][1]
                for b in range(len(bees)): 
                    if b != id:
                        nearestB = coordDist(bees[id],bees[b])
                        if nearestB < 200:
                            for n in range(4):
                                bInFrame = insideRect(tracks[approvedFrames[f]][n][b],tracks[approvedFrames[f]][1][id],200,250)
                                #log.write('checking nearby node '+str(n)+'of bee '+str(b)+'='+str(bInFrame)+u'\n')
                                bCheck.append(bInFrame)
                if True in bCheck:
                   pass
                else: 
                    all.append(approvedFrames[f])
        if self.limitNum == True and len(all) > self.numPerTrack:
            samp = random.sample(all,self.numPerTrack)
            return {id:samp}
        else:
            return {id:all}

    def save(self,id,frame):
        '''actually saves an individual pic of id at frame'''
        filename = pp.getPic(self.vidFile,self.tracks,id,frame,False,self.outPath)
        print('saved image of bee '+str(id)+' on frame '+str(frame))
        return filename 

    def saveId(self,id):
        '''saves all photos for a given ID'''        
        frames = self.getFrames(id)
        frames = frames[id]
        for f in frames:
            saved = self.save(id,f)
            self.photoDict[saved]={'id':id,'frame':f}      

    def saveAll(self):
        '''saves all photos for all tracks in a given video'''
        for t in range(len(self.tracks)):
            self.saveId(t)
        self.writeJson()
    
    def writeJson(self):
      '''creates a json file for writing saved image metadata'''
      init = {'Init':{'VidFile':self.vidFile,'TrackFile':self.trackFile,'Datetime':str(datetime.datetime.now())},'Photos':self.photoDict} 
      with open(self.jsonName,'w') as f:
            json.dump(init,f,indent=2)




##test calling files--------------------------------
#'''
filename = "/home/lqmeyers/SLEAP_files/Bee_vids/2022_06_20_vids/f4x2022_06_20.mp4.predictions.analysis.h5.h" #SLEAP Track File
vidFile = "/home/lqmeyers/SLEAP_files/Bee_vids/2022_06_20_vids/f4x2022_06_20.mp4" #Video SLEAP tracking was performed on

test = photoSet(filename,vidFile)
test.saveAll()
print('saved')
#from track_data_exploratory import showHist
#showHist(test.instScores)
#'''
#----------------------------


