import cv2 
import h5py 
import numpy as np
import math
import os

#-----------Extract h5 data ------------------------------------

def parseTrackData(file):
  '''gets track coords from h5 file '''
  with h5py.File(file,'r') as f:
    #dset_names = list(f.keys())
    #print(dset_names)
    #node_names = f['node_names'][:].T #[b'abdomen' b'waist' b'neck' b'head ']
    #print(node_names)
    locations = f['tracks'][:].T
    #node_names = [n.decode() for n in f['node_names'][:]]
  trackFirst = np.moveaxis(locations,-1,0) #groups by track id
  return trackFirst #locations   

def parseTrackScores(file):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    scores = f['tracking_scores'][:].T
  return scores

def parseInstanceScores(file):
  '''gets track scores from h5 file'''
  with h5py.File(file,'r') as f:
    scores = f['instance_scores'][:].T
  return scores


###--------------------Jeffrey's code--------------------------------------------

#----------All params listed in one spot for easy tweaking-------------------
default_param_dict = {
'width':150, #: Class Attribute for width for plotting 
'height':200, #: Class Attribute for height for plotting 
'scale': 1.0, #: Class Attribute for scale for plotting 
'out_width':None, #: Class Attribute for out_width for plotting 
'out_height':None, #: Class Attribute for out_height for plotting
'cX':None, #: Class Attribute for cX for plotting 
'cY':None, #: Class Attribute for cX for plotting 
'ignore_angle':False, #: Class Attribute for ignore_angle for plotting (this is used to extract images without angle normalization)
'y_offset':0,
}
#----------Helper functions----------------------

#func for finding angle  of body, feed in neck and waist? 
def angleBetweenPoints(p1, p2):
    myradians = math.atan2(p1[0]-p2[0],p1[1]-p2[1])
    mydegrees = math.degrees(myradians)
    return (mydegrees)%360


def rotate_bound2(image,x,y,angle, w,h, cX=None, cY=None, scale=1.0): # I guess this integrates the two funcs? 
    image_size = image.shape[:2]
    M = getRotationMatrix(image_size,x,y,angle, w,h, cX, cY, scale)
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (w, h), flags=cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)


def getRotationMatrix(image_size,x,y,angle, w,h, cX=None, cY=None, scale=1.0): #coulda used rot rect but instead saved as matrix of coords 
    # grab the dimensions of the image and then determine the
    # center
    (h0, w0) = image_size
    (pX, pY) = (x, y) # Rect center in input
    
    if cX is None:
        cX = w / 2     # Rect center in output
        
    if cY is None:
        cY = h / 2     # Rect center in output
    
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, scale) # angle in degrees
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
  # adjust the rotation matrix to take into account translation
    M[0, 2] += pX - cX
    M[1, 2] += pY - cY
    return M


def extract_body(frame, centerX, centerY, angle, width=200, height=400, cX=None, cY=None, scale=1.0, ignore_angle=False): # the actual good one, feeds center and angle to bound2 (still in Class form)
    if ignore_angle:
        angle = 0
    else:
        angle = angle
    return rotate_bound2(frame,centerX,centerY,angle, width, height, cX, cY, scale)


def justFileName(pathIn):
    '''just returns filename from full path str input'''
    # out = ''
    # save = False
    # for c in pathIn[::-1]:
    #   if c == '.':
    #     save = True 
    #   if c == '/':
    #     return out[::-1]
    #   if save == True:
    #     out = out + c
    return(os.path.basename(pathIn[:-4]))

    


#--test file names-------------------------
'''
vidFile = "/mnt/c/Users/lqmey/OneDrive/Desktop/fixed2x6_22_22_test.mp4"
filename = r"/home/lqmeyers/SLEAP_files/h5_files/validation_22_22_6.000_fixed2x6_22_22_test.analysis.h5.h"
frameFolder = "home/lqmeyers/SLEAP_files/Bee_imgs" #need to write out
targetTrack = 2
targetFrame = 175
'''

#---------------main function---------------------

def getPic(vidFile,tracks,targetTrack,targetFrame,param_dict=default_param_dict,show=False,outPath='/home/lqmeyers/SLEAP_files/Bee_imgs/'):
    '''saves a photo of bee from a given track Id (Target Track) at a 
    single frame (TargetFrame) of a video file(VidFile)'''
    #parse track
    bee = tracks[targetTrack][targetFrame][:]
    waist = bee[1]
    neck = bee[2]
    
    #get base frame
    cap = cv2.VideoCapture(vidFile)
    cap.set(cv2.CAP_PROP_POS_FRAMES,targetFrame)
    ret, fullImg = cap.read()

    #crop photo according to params
    width = param_dict['width']
    height = param_dict['height']
    cX = param_dict['cX']
    cY = param_dict['cY']
    scale = param_dict['scale']
    ignore_angle = param_dict['ignore_angle']
    beephoto = extract_body(fullImg,waist[0],waist[1], angleBetweenPoints(waist,neck),width,height,cX,cY,scale,ignore_angle)

    if show == True:
        cv2.imshow('crop',beephoto)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()
    
    #save image
    name = os.path.basename(vidFile)[1:-4]+".mp4.track"+str(targetTrack).zfill(6)+'.frame'+str(targetFrame).zfill(6)+'.png'
    outFile = os.path.join(outPath,name)
    cv2.imwrite(outFile,beephoto)
    return name

#getPic(vidFile,tracks,targetTrack,targetFrame,show=True)



