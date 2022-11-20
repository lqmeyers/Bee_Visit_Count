##File to explore aspects of h5 dataset and write to text file for easy viewing
#Luke Meyers

import h5py 
import numpy as np

#filename = r"//mnt//c//Users//lqmey//Downloads//fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5"
filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h"



 #for writing coords per track 
def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst #locations   

data = parseTrackData(filename)
print(data.shape)

targetTrack = 26

file = open('track_coords.txt','w') #write to txt file to see actual coords per track 
file.write('Coords for track # '+str(targetTrack)+u'\n')
for f in range(len(data[targetTrack])):
  file.write('frame '+str(f)+' coords = '+str(data[targetTrack,f,3,:])+u'\n')
file.close()
print('written')

"""

def parseTrackScores(file):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    dset_names = list(f.keys())
    print(dset_names)
    scores = f['tracking_scores'][:].T#'instance_scores'][:].T
  return scores

data = parseTrackScores(filename)
print(data.shape)
"""

"""
file = open('instance_scores.txt','w')
for f in range(len(data)):
  file.write('frame '+str(f)+' score = '+str(data[f])+u'\n')
file.close()
print('written')
"""

"""-----------------------------------------
#make a histogram of scores 

allScores = []

for i in range(len(data)):
  for val in data[i]:
   if val != np.nan:
    allScores.append(val)

from matplotlib import pyplot as plt 

fig, ax = plt.subplots() 
ax.hist(allScores,30)

plt.show(block=False) #cant find much on what block does but necessarty tpo close 
plt.pause(30) #keeps viewer open 
plt.close() #closes viewer
"""