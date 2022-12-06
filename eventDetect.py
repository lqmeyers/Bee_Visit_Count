##Bringing both drinkin events and visits into one program
#Luke Meyers 7/29/22

import numpy as np 
import h5py
import json 
import math 
from tabulate import tabulate
import datetime

import flowerFinder as ff
import visitDetect as vd 
import drinkingDetect as dd 


def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst


class events:
    def __init__(self,file,vidFile,saveImages=False,FlowerConfigFile='flower_patch_config.json'):
        print('initializing')
        self.file = file 
        self.vidFile = vidFile
        ff.main(vidFile,2,show_validation=False)
        self.configFile = FlowerConfigFile
        self.patchConfig = json.load(open(self.configFile))
        self.tracks = self.getTracks()
        print('track array shape = ',self.tracks.shape)
        print('finding visits')
        self.visits = vd.visits(self.file,self.vidFile,saveImages).visits
        print('finding drinking bees')
        self.drinks = dd.drinks(self.file,self.vidFile,saveImages).drinks
        #print(self.drinks)
        self.analyze()
        print('writing output')
        self.writeJSON()

    def getTracks(self):
        '''seperate tracks from h5'''
        self.tracks = parseTrackData(self.file)
        return self.tracks
   
   
    def analyze(self):
        '''gets useful cumulative numbers'''
        self.visitStatArray = vd.getStats(self.visits,self.patchConfig,self.tracks)
        self.drinkingStatArray = dd.getStats(self.drinks,self.patchConfig,self.tracks)
        self.visitStatDict = vd.makeDict(self.visitStatArray,'stats')
        self.drinkingStatDict = dd.makeDict(self.drinkingStatArray,'stats')

    def writeJSON(self):
        '''writes all info to visits.json'''
        fullDict = {'Init':{'VidFile':self.vidFile,'Datetime':str(datetime.datetime.now())},
            'Visit_Events':{'Visits':vd.makeDict(self.visits),'Statistics':self.visitStatDict},
                    'Drinking_Events':{'Drinks':dd.makeDict(self.drinks),'Statistics':self.drinkingStatDict}}
        with open('events.json','w') as f:
            json.dump(fullDict,f,indent=2)
    
    def displayVisits(self,mode='perFlower'):
        '''display visits in table, mode either perFlower or perIndividual'''
        if mode == 'perFlower':
            '''display table of total visits by flower'''
            flowerDict = self.visitStatDict['Visits_per_Flower']
            for v in range(len(flowerDict)-1):
                flowerDict[v] = [flowerDict[v]]
                flowerDict['Flower '+str(v)] = flowerDict.pop(v)
            print(tabulate(flowerDict,headers='keys',tablefmt='fancy_grid'))
        else:
            '''display table of total visits by individual'''
            listIn = np.ndarray.tolist(self.visitStatArray[1])
            listIn.insert(0,['Track ID','Visits to Flower 0','Visits to Flower 1'])
            print(tabulate(listIn,headers='firstrow',tablefmt='fancy_grid',showindex=True))

    def displayDrinks(self,mode='perFlower'):
        '''display # of drinking events in table, mode either perFlower or perIndividual'''
        if mode == 'perFlower':
            '''display table of total visits by flower'''
            flowerDict = self.drinkingStatDict['Drinks_per_Flower']
            for v in range(len(flowerDict)-1):
                flowerDict[v] = [flowerDict[v]]
                flowerDict['Flower '+str(v)] = flowerDict.pop(v)
            print(tabulate(flowerDict[:-1],headers='keys',tablefmt='fancy_grid'))
        else:
            '''display table of total visits by individual'''
            listIn = np.ndarray.tolist(self.drinkingStatArray[1])
            listIn.insert(0,['Track ID','Drinking Events at Flower 0','Drinking Events at Flower 1'])
            print(tabulate(listIn,headers='firstrow',tablefmt='fancy_grid',showindex=True))

    ##ADD WRITE TO CSV!!!

    def displayEvents(self,mode='perFlower'):
        if mode == 'perFlower':
            fullFlowerDict = {'Event Type':['Drinking Nectar','Flower Visits']}
            flowerVisitDict = self.visitStatDict['Visits_per_Flower']
            flowerDrinkDict = self.drinkingStatDict['Drinks_per_Flower']
            for v in range(len(flowerDrinkDict)):
                fullFlowerDict[v] = [flowerDrinkDict[v],flowerVisitDict[v]]
                fullFlowerDict['Flower '+str(v)] = fullFlowerDict.pop(v)
            print(tabulate(fullFlowerDict,headers='keys',tablefmt='fancy_grid'))
        else: 
            '''display table of total visits by individual'''
            combinedList = []
            for i in range(len(self.visitStatArray[1])):
                combinedList.append(np.ndarray.tolist(self.visitStatArray[1][i])+np.ndarray.tolist(self.drinkingStatArray[1][i]))
            combinedList.insert(0,['Track ID','Visits to Flower 0','Visits to Flower 1','Drinks at Flower 0','Drinks at Flower 1'])
            print(tabulate(combinedList,headers='firstrow',tablefmt='fancy_grid',showindex=True))


#----------------Test Calls ----------------------------------


#test calls for 2x6_22_22 vid ------------
#filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h"
#vid = "/mnt/c/Users/lqmey/OneDrive/Desktop/fixed2x6_22_22_test.mp4"

filename = "/home/lqmeyers/SLEAP_files/h5_files/fixed3x6_22_22_test.mp4.predictions.analysis.h5.000_fixed3x6_22_22_test.analysis.h5"
vid = "/home/lqmeyers/SLEAP_files/Bee_vids/22_6_22_vids/fixed3x6_22_22_test.mp4"

e = events(filename,vid,True)
e.displayEvents()

