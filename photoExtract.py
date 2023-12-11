
import sys 
from matplotlib import pyplot as plt 

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

from photos import photoSet

trackFile = sys.argv[1]
vidFile = sys.argv[2]
config_file = sys.argv[3]


sys.stdout = open(1, 'w')

p = photoSet(trackFile,vidFile,config_file)
p.saveAll()
print('saved')


