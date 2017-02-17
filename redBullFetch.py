import os
import subprocess
from PIL import Image
from tesserocr import image_to_text

def splitVideo(avFile, interval=200 ,saveDir=os.getcwd() + '/screens'):
    # interval is in milliseconds - convert to fps
    fps = '%f' % (10**3 / interval)

    # check if save directory exists. create it if not
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    # generate screencaptures
    subprocess.run(['ffmpeg', '-i', './' + avFile, '-vf', 'fps=' + fps,
        saveDir + '/img%05d.bmp']) 

    return

def processScreenCap(screenCaptureObj):

    timeImg = screenCaptureObj.crop((589,659,750,698))
    altitudeImg =                   # in m 
    speedImg =                      # in kph 
    heartImg =                      # in bpm
    respirImg =                     # respiration in ???

    time = image_to_text(timeImg)



if __name__ == '__main__':
    import sys

#    videoPath = sys.argv[1]

#    print('Generating frames ...')
#    splitVideo(videoPath)
#    print('Done ...')

    screen = Image.open('./screens/img000001.bmp')

    processScreenCap(screen)
