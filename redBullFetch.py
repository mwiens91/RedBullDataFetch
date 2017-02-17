import os
import subprocess
import re
import csv
from PIL import Image
from tesserocr import image_to_text

def generateScreenCaps(avFile, interval=200,
                screenDir=os.getcwd() + '/screens'):
    # Interval is in milliseconds - convert to fps
    fps = '%f' % (10**3 / interval)

    # Check if save directory exists; create it if not
    if not os.path.exists(screenDir):
        os.makedirs(screenDir)

    # Check if save directory is empty; abort if not
    if not os.listdir(screenDir):
        print(screenDir + ' is not empty!')
        print('Empty it out before running this!')
        return False

    # Generate screencaptures ussing ffmpeg
    subprocess.run(['ffmpeg', '-i', './' + avFile, '-vf', 'fps=' + fps,
        screenDir + '/img%05d.bmp']) 

    return True

def processScreenCap(screenCaptureObj):

    # Extract subset of image corresponding to data
    timeImg = screenCaptureObj.crop((585,662,749,698))
    altitudeImg = screenCaptureObj.crop((1359,226,1464,254))    # in m
    speedImg = screenCaptureObj.crop((1665,226,1764,256))       # in kph 
    heartImg = screenCaptureObj.crop((1368,526,1460,555))       # in bpm
    respirImg = screenCaptureObj.crop((1356,565,1463,594))      # respiration
                                                                # in ????

    # Extract text from images using Tesseract OCR
    time = image_to_text(timeImg)
    altitude = image_to_text(altitudeImg)
    speed = image_to_text(speedImg)
    heart = image_to_text(heartImg)
    respir = image_to_text(respirImg)

    # Strip trailing whitespace Tesseract OCR seems to pick up 
    time = time.rstrip()
    altitude = altitude.rstrip()
    speed = speed.rstrip()
    heart = heart.rstrip()
    respir = respir.rstrip()

    # Convert the time to seconds
    matchTime = re.match(
        r'^(?P<sign>-?)(?P<mins>\d+):(?P<secs>\d+)\.(?P<msecs>\d+)$', time)
    timePretty = float(matchTime.group('mins')) * 60 + float(matchTime.group('secs'))
        + float(matchTime.group('msecs')) * 10**(-3)

    # In the video time is negative before the jump
    if matchTime.group('sign')
        timePretty *= -1

    return (timePretty, altitude, speed, heart, respir)

def parseScreenCaptures(csvFile, screenDir=os.getcwd() + '/screens'):
    

    

if __name__ == '__main__':
    import sys

    videoPath = sys.argv[1]

    print("Generating screencaptures . . .")

#    if not generateScreenCaps(videoPath):       # exit if something went amiss 
#        print("Exiting script . . . ")
#        sys.exit(0)

    print("Done")

    print("Writing to CSV . . . ")


    screen = Image.open('./screens/img000001.bmp')

    print(processScreenCap(screen))
