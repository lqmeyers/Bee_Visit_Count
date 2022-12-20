import json 
import os 
import sys 

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

##A python script to intake a filename and id and annote that id in a json 

imgPath = sys.argv[1]
id = sys.argv[2]

def getName(file):
    '''uses a path string to get the name of a file'''
    strOut = ''
    i = 1
    while file[-i] != '/':
        i = i + 1
        #print(file[-i])
    strOut = file[-(i-1):]
    return strOut

def getPath(file):
    '''uses a path string to get just the directoy of a file'''
    strOut = ''
    i = 1
    while file[-i] != '/':
        i = i + 1
        #print(file[-i])
    strOut = file[0:len(file)-(i-1)]
    return strOut

imgName = getName(imgPath)
imgFold = getPath(imgPath)


annotatedDict = json.load(open(imgFold+'annotated.json'))

photoDict = annotatedDict['Photos']
print(photoDict)

photoDict[imgName]={'id':id}
print(photoDict)
annotatedDict['Photos']=photoDict

print(annotatedDict)


with open(imgFold+'annotated.json','w') as f:
        json.dump(annotatedDict,f,indent=2)