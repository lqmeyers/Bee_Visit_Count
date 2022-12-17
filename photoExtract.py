
import sys 
from matplotlib import pyplot as plt 

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

from photos import photoSet

trackFile = sys.argv[1]
vidFile = sys.argv[2]


sys.stdout = open(1, 'w')

p = photoSet(trackFile,vidFile)
p.saveAll()
print('saved')


