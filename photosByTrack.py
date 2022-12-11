import cv2 
import h5py 
import numpy as np
import math
import sys 
import json

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')
import profilePic as pp 
from getBestFrame import bestFrame

#------------helper functions------------------ 
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



def main(trackFile,vidFile,outputPath,writelog=False):
  '''Saves one photo of bee per event from json file  
  ##need to finish adding option to write logs into subfunctions, for now just uncomment folks
  '''
  
  iScores = parseTrackScores(trackFile)
  tScores = parseTrackScores(trackFile,'tracks')
  tracks = parseTrackData(trackFile)

  video_in = cv2.VideoCapture(vidFile)
  length = int(video_in.get(cv2.CAP_PROP_FRAME_COUNT))

  start = 0
  end = length-1
  for t in range(len(tracks)): 
    targetFrame = bestFrame(start,end,t,tracks,iScores,tScores,'less_clean')
    if targetFrame != 0:
        pp.getPic(vidFile,tracks,t,targetFrame,False,outputPath)
        print('actually saved')
    print('done!')




##------------calling the func---------------------------------------

filename = r"/home/lqmeyers/SLEAP_files/h5_files/f22x2022_06_28.mp4.predictions.analysis.h5.h" #SLEAP Track File
vidFile = "/home/lqmeyers/SLEAP_files/Bee_vids/2022_06_28_vids/f22x2022_06_28.mp4" #Video SLEAP tracking was performed on

main(filename,vidFile,'/home/lqmeyers/SLEAP_files/Bee_imgs/')