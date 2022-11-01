##File to explore aspects of h5 dataset and write to text file for easy viewing
#Luke Meyers

import h5py 
import numpy as np

#filename = r"//mnt//c//Users//lqmey//Downloads//fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5"
filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h"



''' #for writing coords per track 
def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst #locations   

data = parseTrackData(filename)
print(data.shape)

targetTrack = 6

file = open('track_coords.txt','w') #write to txt file to see actual coords per track 
for f in range(len(data[targetTrack])):
  file.write('frame '+str(f)+' coords = '+str(data[targetTrack,f,3,:])+u'\n')
file.close()
print('written')
'''

def parseTrackScores(file):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    scores = f['tracking_scores'][:].T
  return scores

data = parseTrackScores(filename)
print(data.shape)

file = open('track_scores.txt','w')
for f in range(len(data)):
  file.write('frame '+str(f)+' score = '+str(data[f])+u'\n')
file.close()
print('written')