import cv2 
import h5py 
import numpy as np
import math
import sys 
import json

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')
import profilePic as pp 
from getBestFrame import bestFrame


def parseTrackData(file):
  '''gets track coords from h5 file '''
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    #print(dset_names)
    #node_names = f['node_names'][:].T #[b'abdomen' b'waist' b'neck' b'head ']
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

def main(trackFile,vidFile,jsonFile,outputPath,writelog=False):
  '''Saves one photo of bee per event from json file  
  ##need to finish adding option to write logs into subfunctions, for now just uncomment folks
  '''
  iScores = parseTrackScores(trackFile)
  tScores = parseTrackScores(trackFile,'tracks')
  tracks = parseTrackData(trackFile)
  drinking = open(jsonFile)
  drinks = json.load(drinking)
  drinks = drinks['Drinking_Events']
  if writelog == True:
    log = open('photoTestLog.txt','w')
  for i in range(len(drinks)):
      d = drinks[str(i)]
      #log.write(str(d)+u'\n')
      start = d['start_frame']
      end = d['end_frame']
      trackId = d['track_id']
      targetFrame = bestFrame(start,end,trackId,tracks,iScores,tScores)
      #log.write('Frame chosen ='+str(targetFrame)+u'\n')
      if targetFrame != 0:
        pp.getPic(vidFile,tracks,trackId,targetFrame,False,outputPath)
  print('All done')
  if writelog == True:
    log.close()
    print('written')


##------------calling the func---------------------------------------

filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h" #SLEAP Track File
vidFile = "/home/lqmeyers/SLEAP_files/Bee_vids/22_6_22_vids/fixed2x6_22_22_test.mp4" #Video SLEAP tracking was performed on
drinkingjson = '/mnt/c/Users/lqmey/OneDrive/Desktop/Bee_Visit_Count/drinks.json' #visits json created by running event detect 

main(filename,vidFile,drinkingjson,'/home/lqmeyers/SLEAP_files/Bee_imgs/test/')