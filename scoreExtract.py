
import sys 
import h5py
from matplotlib import pyplot as plt 
import numpy as np 

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')


trackFile = sys.argv[1]
scoreType = sys.argv[2]

sys.stdout = open(1, 'w')


def parseTrackScores(file,scoretype):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    dset_names = list(f.keys())
    #print(dset_names)
    if scoretype == 'instance':
        scores =  f['instance_scores'][:].T##switch these around
    elif scoretype == 'tracks':
        scores = f['tracking_scores'][:].T #
    else:
       print("Invalid type request")
  return scores


data = parseTrackScores(trackFile,scoreType)

'''creates a histogram of a set of data'''

allScores = [] #filter null values
for i in range(len(data)):
    for val in data[i]:
        if val != np.nan and val > 0:
          allScores.append(val)

#print(allScores)
from matplotlib import pyplot as plt 

fig, ax = plt.subplots() 
ax.hist(allScores,30)
ax.set_xlabel(scoreType+' score')
ax.set_ylabel('Number of detections')
ax.set_title(scoreType+' scores of '+trackFile)


plt.savefig((trackFile+'.'+scoreType+'.scores.png'))
print('saved')

#plt.show(block=False) #cant find much on what block does but necessarty tpo close 
#plt.pause(30) #keeps viewer open 
#plt.close() #closes viewer



