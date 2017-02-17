import os
import subprocess
import csv
from PIL import Image
from tesserocr import image_to_text

def generateScreenCaps(avFile, interval=200
        ,screenDir=os.getcwd() + '/screens'):
    # Interval is in milliseconds - convert to fps
    fps = '%f' % (10**3 / interval)

    # Check if save directory exists; create it if not
    if not os.path.exists(screenDir):
        os.makedirs(screenDir)

    # Generate screencaptures ussing ffmpeg
    subprocess.run(['ffmpeg', '-i', './' + avFile, '-vf', 'fps=' + fps,
        screenDir + '/img%05d.bmp']) 

    return

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

    return (time, altitude, speed, heart, respir)

def parseScreenCaptures(csvFile, screenDir=os.getcwd() + '/screens'):
    

if __name__ == '__main__':
    import sys

    videoPath = sys.argv[1]

    print("Generating screencaptures . . .")
    generateScreenCaps(videoPath)
    print("Done")

    print("Writing to CSV . . . ")


    screen = Image.open('./screens/img000001.bmp')

    print(processScreenCap(screen))
