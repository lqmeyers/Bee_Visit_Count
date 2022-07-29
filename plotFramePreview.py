##Ok lets try using keyboard 
#Luke Meyers 7/1/22


import sys
#sys.path.insert(1,r'C:\Users\lqmey\AppData\Local\Programs\Python\Python39')
sys.path.insert(1,r'C:\Users\lqmey\OneDrive\Desktop\Python Code\PlotBee_Analysis')



from matplotlib import pyplot as plt 
from matplotlib import patches as ptch
import matplotlib.image as mpimg
import cv2
import flowerFinder as ff


#------initalize files------------------

#vidFile = 'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/20_6_22_vids/fixed5x6_20_22_test.mp4'
#vidFile = r"C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\20_6_22_vids\fixed2x6_20_22_test.mp4"
vidFile = r"C:\Users\lqmey\OneDrive\Desktop\Bee Videos\test in feild\22_6_22_vids\fixed3x6_22_22_test.mp4"
frameFile = r'C:/Users/lqmey/OneDrive/Desktop/Bee Videos/test in feild/22_6_22_vids/targetFrame.tiff'

cap = cv2.VideoCapture(vidFile)


#save frame to same loc as file--------------
def getDir(file):
    '''uses a path string to get the parent dir of a file'''
    strOut = ''
    i = 0 
    while file[-i] != '/' :
        i = i + 1 
        #print(file[-i])
    strOut = file[0:-i]
    return strOut

def switchFrame(event):
    global fid #need global becuase we're setting it
    if event.key == 'right':
        fid = fid+1
    elif event.key == 'left':
        fid = fid-1
    update(cap,fid)
    print(fid)
    

def getFrame(cap,id):
    '''when called saves frame based on id from video to file called targetFrame'''
    print(cap)
    #cap.set(cv2.CAP_PROP_POS_FRAMES,id)
    ret, frame = cap.read()
    #frameDir = str(getDir(video))
    #frameFile = frameDir+'targetFrame.tiff' 
    #cv2.imwrite(frameFile,frame)
    return frame
#link numpy from getFrame to update 

def update(cap,id):
    '''refreshes image plot for current frame id and plots 
    bounds of critical area'''
    #plot.clear()
    img = getFrame(cap,id)
    img = img[...,[2,1,0]]
    #img = mpimg.imread(frameFile)
    #print(img.shape)
    imageplot = ax.imshow(img)
    ax.add_artist(rect1)
    ax.add_artist(rect2)
    plt.show()

#--- do it the first time 
fid = 3425#rect2 = ptch.Rectangle((590,480),100,100,fill=False,lw=1) #set frame id that will be changed 
getFrame(cap,fid) #writes to frameFile 

whiteCenter = ff.main(frameFile,2,'center',show_validation=False)[0]
blueCenter = ff.main(frameFile,2,'center',show_validation=False)[1]

#---generate figure and show 
fig, ax = plt.subplots()

#rect1 = ptch.Rectangle((1330,450),100,100,fill=False,lw=1) #recangles 
#rect2 = ptch.Rectangle((590,480),100,100,fill=False,lw=1)

rect1 = ptch.Circle(whiteCenter,radius=50,fill=False,lw=1) #circles act 
rect2 = ptch.Circle(blueCenter,radius=50,fill=False,lw=1)

k = fig.canvas.mpl_connect('key_press_event',switchFrame) #set keypress event 

plt.show()

#print('ran')




