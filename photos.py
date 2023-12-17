## a complete script for extracting all the photos from a video
import h5py 
import datetime
import numpy as np
import math
import sys 
import json
import random
from matplotlib import pyplot as plt 
import yaml
import pandas as pd 
import os
import cv2

sys.path.insert(0, '/mnt/c/Users/lqmey/OneDrive//Desktop/Bee_Visit_Count/')

import profilePic as pp 
#import flowerFinder as ff
#import visitDetect as vd 
#import drinkingDetect as dd 


##funcs used for data handling (eventually will be made into utils.py)

def parseTrackData(file):
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst

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


def insideRect(coords,center,w,h):
  '''returns true if inside, returns false if not'''
  #center = [1380,480]
  xBound = w/2
  yBound = h/2
  allcoords = []
  x = coords[0] 
  y = coords[1]
  if x >= center[0]-xBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if x <= center[0]+xBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y >= center[1]-yBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if y <= center[1]+yBound:
    allcoords.append(True)
  else: 
    allcoords.append(False)
  if False in allcoords:
    return False
  else: 
    return True 

def coordDist(coord1,coord2):
  '''computes the distance between two coordinates inputed as tuples'''
  x1 = coord1[0]
  y1 = coord1[1]
  x2 = coord2[0]
  y2 = coord2[1]
  a = abs(x2-x1)
  b = abs(y2-y1)
  c = math.sqrt((a**2)+(b**2))
  return abs(c)

  
def getName(file):
    '''uses a path string to get the name of a file'''
    strOut = ''
    i = 1
    while file[-i] != '/':
        i = i + 1
        #print(file[-i])
    strOut = file[-i:]
    return strOut

##---------------photo class----------------------------------

##---Class to contain all functions and extracted data for a set of photos from a video
class photoSet:
    def __init__(self,trackFile,vidFile,config_file='/home/lmeyers/Bee_Visit_Count/photoExtractConfig.yml'):
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
                self.config = config
            seed = config['random_seed']
            self.verbose = config['verbose']
            out_path = config['out_dir_path'] #: '/home/lmeyers/Bee_imgs_test/' #directory to save extracted images to
            random_sample = config['random_sample'] #: True 
            num_imgs_per_track = config['num_imgs_per_track']
            clean = config['clean_photos']#: True
            min_bee_dist = config['min_bee_distance'] #: 200
            filtering = config['filter_by_score'] #: True
            min_inst_score = config['min_instance_score'] #: 
            min_track_score = config['min_track_score']
            self.photo_params = config['photo_params']
        except Exception as e:
            print('ERROR - unable to open experiment config file. Terminating.')
            print('Exception msg:',e)
            return -1
        
        #set random seed
        random.seed(seed)
        
        #initialize datafiles, configs, and paths
        self.trackFile = trackFile 
        self.vidFile = vidFile
        self.vid_obj = cv2.VideoCapture(vidFile) #open video once 
        
        #Extract data from h5 file 
        self.tracks = self.getTracks()
        self.instScores = self.getScores()
        self.trackScores = self.getScores('tracks')
        
        #Set photo filtering criteria
        self.cleanliness(clean)
        if filtering == True:
          self.setLimits(min_inst_score,min_track_score,min_bee_dist) #these are estimated arbitrarily rn but could be automated later
        else:
          self.setLimits(0.0,0.0)
        
        #Set sample number per track
        if random_sample == True:
          self.setNumPerTrack(num_imgs_per_track)
        else:
          self.limitNum = False

        #Destination folder
        if not os.path.exists(out_path):
           os.mkdir(out_path)
        self.setOutPath(out_path)

        #Documentation files
        self.jsonName = (os.path.basename(self.vidFile)[1:]+(datetime.datetime.now().strftime('.%d.%m.%Y.%H.%M.%S.')+'photolog.json'))
        self.jsonPath = os.path.join(self.outPath,self.jsonName)
        self.photoDict = {}
        self.photo_dataframe = pd.DataFrame(columns=['vid_file','track_file','frame','track_id','tracking_score','instance_score'])
       

    def getTracks(self):
        '''seperate tracks from h5'''
        self.tracks = parseTrackData(self.trackFile)
        return self.tracks
    
    def getScores(self,mode='instance'):
        '''seperates scores from h5'''
        self.scores = parseTrackScores(self.trackFile,mode)
        return self.scores

    def setLimits(self,instanceScore,trackScore,beeDist=200):
        '''inits score threshold for saving photos'''
        self.minInstScore = instanceScore
        self.minTrackScore = trackScore
        self.minBeeDist = beeDist
    
    def setInterval(self,interval):
        '''determines frame interval between repeat captures'''
        self.interval = interval

    def setNumPerTrack(self,num):
        '''set number of repeat imgs per track'''
        self.numPerTrack = num
        self.limitNum = True

    def setOutPath(self,path='/home/lqmeyers/SLEAP_files/Bee_imgs/'):
        '''sets outpath for writing images, if you need to specify'''
        self.outPath = path

    def cleanliness(self,mode):
        '''determines if other bees are allowed in frame'''
        self.cleanliness = mode

    def getFrames(self,id):
        '''scans through all frames of an np array and returns a list of ones worth saving as a dictionary item with the
        track id'''
        approvedFrames = [] 
        for f in range(len(self.tracks[id])):
            if self.trackScores[f][id] > self.minTrackScore and self.instScores[f][id]  > self.minInstScore:
              cCheck = True
              for coord in self.tracks[id][f]:
                for x in coord:
                  if x <= 0: #getting rid of ones where not all key points were detected. 
                    cCheck = False
              if cCheck == True: 
                approvedFrames.append(f)
        if self.cleanliness == True: #if removing other bees in frame
            trackLast = np.moveaxis(self.tracks,0,-1)
            tracks = np.moveaxis(trackLast,-1,2) #change shape from format expectec in most other functions 
            all = [] 
            for f  in range(len(approvedFrames)):
                bCheck = []
                bees = tracks[approvedFrames[f]][1]
                for b in range(len(bees)): 
                    if b != id:
                        nearestB = coordDist(bees[id],bees[b])
                        if nearestB < self.minBeeDist: 
                            for n in range(4): #checks all key points 
                                bInFrame = insideRect(tracks[approvedFrames[f]][n][b],tracks[approvedFrames[f]][1][id],150,200)#previously 200,250
                                #log.write('checking nearby node '+str(n)+'of bee '+str(b)+'='+str(bInFrame)+u'\n')
                                bCheck.append(bInFrame)
                if True in bCheck:
                   pass #filters by removing frames where nearest bee is less than 200 pixels away 
                else: 
                    all.append(approvedFrames[f])
        if self.limitNum == True and len(all) > self.numPerTrack:
            samp = random.sample(all,self.numPerTrack)
            return {id:samp}
        else:
            return {id:all}

    def save(self,id,frame):
        '''actually saves an individual pic of id at frame'''
        filename = pp.getPic(self.vidFile,self.vid_obj,self.tracks,id,frame,self.photo_params,False,outPath=self.outPath)
        print('saved image of bee '+str(id)+' on frame '+str(frame))
        return filename 

    def saveId(self,id):
        '''saves all photos for a given ID'''        
        frames = self.getFrames(id)
        frames = frames[id]
        for f in frames:
            saved = self.save(id,f)
            bee = self.tracks[id][f]
            #add background color detection and edge annotation here
            self.photoDict[saved]={'id':id,
                                   'frame':f,
                                   'tracking_score':self.trackScores[f][id],
                                   'instance_score':self.instScores[f][id],
                                   'pose':bee.tolist(),  #this may need to be changed incase skeleton changes                                  
    } 
            
    def writeId(self,id):
      '''writes a line to out_dataframe for each image to be saved from track ID'''
      frames = self.getFrames(id)
      frames = frames[id]
      for f in frames:
        bee = self.tracks[id][f]
        bee = bee.tolist()
        row = len(self.photo_dataframe)
        self.photo_dataframe.loc[row] = {'vid_file':self.vidFile,'track_file':self.trackFile,
                                                                'frame':f,'track_id':id,'tracking_score':self.trackScores[f][id],
                                                                'instance_score':self.instScores[f][id]}
        for kp in range(4):
          col_name = 'keypoint '+str(kp)
          val = str(bee[kp])
          self.photo_dataframe.loc[row,col_name] = val

    def saveAll(self):
        '''saves all photos for all tracks in a given video'''
        for t in range(len(self.tracks)):
            self.saveId(t)
        self.writeJson()
    
    def writeALL(self,out_csv_path):
      '''writes all images to be saved to a dataframe and to a csv'''
      for t in range(len(self.tracks)):
          self.writeId(t)
      self.photo_dataframe.to_csv(out_csv_path,index=False)

    def writeJson(self):
      '''creates a json file for writing saved image metadata'''
      #init = {'Init':{'VidFile':self.vidFile,'TrackFile':self.trackFile,'Datetime':str(datetime.datetime.now()),'Criteria':{'tracking_score':self.minTrackScore,'instance_score':self.minInstScore,'dist_to_other_bees':self.minBeeDist}},'Photos':self.photoDict} 
      init = {'init':{'vid_file':self.vidFile,'track_file':self.trackFile,'date_of_extraction':str(datetime.datetime.now()),'configs':self.config},'photos':self.photoDict} 
      with open(self.jsonPath,'w+') as f:
            json.dump(init,f,indent=2)


def save_images_from_dataframe(in_csv,config_file):
    '''saves images based on rows in a dataframe containing:
    video path, trackfile, frame, track id, using the params in photo config file '''  
    
    df = pd.read_csv(in_csv)
    df.groupby('vid_file')
    df_out = df
    # Dictionary to cache opened files
    file_cache = {}

    with open(config_file) as f:
                            config = yaml.safe_load(f)            
    out_path = config['out_dir_path'] #: '/home/lmeyers/Bee_imgs_test/' #directory to save extracted images t
    photo_params = config['photo_params']
    dataframe_configs = config['dataframe_configs']
    
    video_col_name = dataframe_configs['video_col_name']
    track_col_name = dataframe_configs['track_col_name']
    track_id_col_name = dataframe_configs['track_id_col_name']
    frame_col_name = dataframe_configs['frame_col_name']

    row_index = 0 
    # Iterate through DataFrame rows
    for index, row in df.iterrows():        
        
        vid_file_path = row[video_col_name]
        track_file_path = row[track_col_name]
        id = row[track_id_col_name]
        frame = row[frame_col_name]

        # Check if vid file is already opened
        if vid_file_path not in file_cache:
            #vid_file = open(vid_file_path, 'rb')
            vid_file = cv2.VideoCapture(vid_file_path)
            file_cache[vid_file_path] = vid_file #right now this doesnt exactly matter cause getPic opens vidFile
        else:
            vid_file = file_cache[vid_file_path]

        # Check if track file is already opened
        if track_file_path not in file_cache:
            #track_file = open(track_file_path, 'r')
            tracks = parseTrackData(track_file_path)
            file_cache[track_file_path] = tracks
        else:
            tracks = file_cache[track_file_path]
        
        filename = pp.getPic(vid_file_path,vid_file,tracks,id,frame,photo_params,False,outPath=out_path)
        print('saved image of bee '+str(id)+' on frame '+str(frame))
        df_out.loc[row_index,'photo_file_path'] = filename
        df_out.loc[row_index,photo_params.keys()] = photo_params.values()

        
        row_index += 1

    df_out.to_csv(in_csv[:-4]+'.saved.csv',index=False)
 
   



##test calling files--------------------------------
'''
filename = "/home/lmeyers/SLEAP_files/Bee_vids/2022_06_20_vids/f7x2022_06_20.mp4.predictions.analysis.h5.h" #SLEAP Track File
vidFile = "/home/lmeyers/SLEAP_files/Bee_vids/2022_06_20_vids/f7x2022_06_20.mp4" #Video SLEAP tracking was performed on

test = photoSet(filename,vidFile)
test.setLimits(.81,.15,150)
test.setOutPath('/home/lqmeyers/SLEAP_files/Bee_imgs/filesort/')
test.setNumPerTrack(50)
#test.saveId(1)
test.writeALL('/home/lmeyers/Bee_imgs_test/out_test.csv')

save_images_from_dataframe('/home/lmeyers/Bee_imgs_test/out_test.csv','/home/lmeyers/Bee_Visit_Count/photoExtractConfig.yml')
#test.saveAll()
print('saved')
#from track_data_exploratory import showHist
#showHist(test.instScores)
#'''
#----------------------------


