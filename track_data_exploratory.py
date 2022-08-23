##File to explore aspects of h5 dataset and write to text file for easy viewing
#Luke Meyers

import h5py 
import numpy as np

filename = r'C:\Users\lqmey\Downloads\fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5'

def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  #trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return locations #trackFirst

data = parseTrackData(filename)
print(data.shape)

"""
file = open('track_coords.txt','w') #write to txt file to see actual coords per track 
for f in range(len(data[380])):
  file.write('frame '+str(f)+' coords = '+str(data[377,f,3,:])+u'\n')
file.close()
print('written')
"""