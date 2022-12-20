import sys 
import cv2

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')


imgFile = sys.argv[1]

img = cv2.imread(imgFile)
cv2.imshow('display',img)
cv2.waitKey(20000)
cv2.destroyAllWindows()

sys.stdout = open(1, 'w')




