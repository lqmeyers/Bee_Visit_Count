##score greater than 1 

#load in files and dependencies. Make sure path is accurate

import cv2 
import h5py 
import numpy as np
import math
import sys 
import json

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

import profilePic as pp 

def parseTrackData(file):
  '''gets track coords from h5 file '''
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    #print(dset_names)
    node_names = f['node_names'][:].T #[b'abdomen' b'waist' b'neck' b'head ']
    #print(node_names)
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst #locations 

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

def averageList(listIn): 
  '''returns the mean of a list'''
  sum = 0
  num = 0 
  for i in listIn:
    if type(i) == int or float:
      sum = sum + i 
      num = num + 1 
  return (sum/num)

def lowest(listIn):
  '''returns the lowest in a list'''
  lowest = 2000 #because of resolution this is kinda the upper limit 
  for i in listIn:
    #if type(i) == int or float:
    if i < lowest:
      lowest = i 
  return lowest 



def bestFrame(start,end,id,tracks,instanceScores,trackScores,mode='extra_clean'):
  '''recives a range of frams and picks best frames to take pics of 
  track id from video'''
  trackLast = np.moveaxis(tracks,0,-1)
  tracks = np.moveaxis(trackLast,-1,2) #change shape from format expectec in most other functions
  frames = list(range((end-start)))
  above1 = []
  bestDist = 0
  bestFrame = 0
  for f in frames: 
    if trackScores[start+f][id] > .2 and instanceScores[start+f][id]  > .99: #filter based on track and instance confidence 
      above1.append(f)
  for t in above1:
    dists = [] 
    bCheck = []
    #log.write('Grading frame '+str(start+t)+u'\n')
    bees = tracks[start+t][2]
    for b in range(len(bees)): 
      if b != id:
        nearestB = coordDist(bees[id],bees[b])
        dists = dists + [nearestB]
        if mode =='extra_clean': #if no other bees allowed in frame
          if nearestB < 200:
            for n in range(4):
              bInFrame = insideRect(tracks[start+t][n][b],tracks[start+t][1][id],200,250)
              #log.write('checking nearby node '+str(n)+'of bee '+str(b)+'='+str(bInFrame)+u'\n')
              bCheck.append(bInFrame)
    nearest = (lowest(dists))
    if True in bCheck:
        break
    if nearest > bestDist: #picks the frame where the nearest bee in the farthest away
      bestDist = nearest
      bestFrame = start+t
  return bestFrame  


