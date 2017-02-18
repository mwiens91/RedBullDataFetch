import os
import subprocess
import re
import csv
from PIL import Image
from PIL import ImageEnhance
from tesserocr import image_to_text

def generateScreenCaps(avFile, interval=200,
                        screenDir=os.getcwd() + '/screens'):

    # Interval is in milliseconds - convert to fps
    fps = '%f' % (10**3 / interval)

    # Check if save directory exists; create it if not
    if not os.path.exists(screenDir):
        os.makedirs(screenDir)

    # Check if save directory is empty; abort if not
    if os.listdir(screenDir):
        print(screenDir + ' is not empty!')
        print('Empty it out before running this!')
        return False

    # Generate screencaptures using ffmpeg
    subprocess.run(['ffmpeg', '-i', './' + avFile, '-vf', 'fps=' + fps,
        screenDir + '/img%08d.bmp'])

    return True


def processScreenCap(screenCaptureObj):

    # Extract subset of image corresponding to data
    timeImg = screenCaptureObj.crop((585,662,749,698))
    altitudeImg = screenCaptureObj.crop((1359,226,1464,254))    # in m
    speedImg = screenCaptureObj.crop((1665,226,1764,256))       # in kph 
    heartImg = screenCaptureObj.crop((1368,526,1460,555))       # in bpm
    respirImg = screenCaptureObj.crop((1356,565,1463,594))      # respiration
                                                                # in ????

    # Sharpen images for more accurate OCR readings
    # The time has a semitransparent moving background,
    # making text recognition difficult
    #
    # I've kind of haphazardly determined that these settings
    # result in an improvement of text recognition, but doubtless
    # there are better modifications
    timeImg = timeImg.convert('L')
#    timeImg = ImageEnhance.Contrast(timeImg)
#    timeImg = timeImg.enhance(10)
#    timeImg = ImageEnhance.Sharpness(timeImg)
#    timeImg = timeImg.enhance(2)
    altitudeImg = altitudeImg.convert('L')
    speedImg = speedImg.convert('L')
    heartImg = heartImg.convert('L')
    respirImg = respirImg.convert('L')

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

    # Split time string into components
    matchTime = re.match(
        r'^(?P<sign>-?)(?P<mins>\d+):(?P<secs>\d+)\.(?P<msecs>\d+)$', time)

    # Return the data points if everything is okay. Otherwise
    # return false
    try:
        # A number of sanity checks follow. Sometimes
        # errors sneak in, so it's good to overly cautious here
        if (len(heart) != 3 or
            len(respir) != 2 or
            len(speed) == 0 or
            len(matchTime.group('mins')) != 2 or
            len(matchTime.group('secs')) != 2 or
            len(matchTime.group('msecs')) != 3
            ):
            raise AttributeError('Bad data')

        # Convert time components into seconds
        timePretty = (float(matchTime.group('mins')) * 60
                + float(matchTime.group('secs'))
                + float(matchTime.group('msecs')) * 1e-3)

        # In the video time is negative before the jump
        if matchTime.group('sign') == '-':
                timePretty *= -1

        return (timePretty, altitude, speed, heart, respir)
    except AttributeError:
        # Such error! OCR failed!
        return False


def writeScreenCapData(screenDir=os.getcwd() + '/screens',
                        dataSheetFile='./data.csv'):

    # Open a datasheet
    # If the file given in the argument dataSheetFile exists,
    # prompt for a new file path until there isn't a conflict.

    # I could just exit the program here, but then that risks
    # losing a LOT of image files (since the script is currently
    # set up only to run from a clean slate); so even though
    # this is annoying, I feel like it's a necessary annoyance
    while os.path.isfile(dataSheetFile):
        print(dataSheetFile + " already exists!")
        print("Enter the relative path for the datasheet:")
        dataSheetFile = input("> ")

    dataFile = open(dataSheetFile, 'w')
    dataWriter = csv.writer(dataFile)

    # Write headings to the data sheet 
    dataWriter.writerow(('Time (s)', 'Altitude (m)', 'Speed (kph)',
        'Heart rate (bpm)', 'Respiration (???)'))

    # Get all screencapture filenames
    screenCaps = os.listdir(screenDir)
    screenCaps.sort()
    
    # Process each screencapture
    errorCount = 0
    successCount = 0
    for cap in screenCaps:
        with Image.open(screenDir + '/' + cap) as capObj:
            imgData = processScreenCap(capObj)

            if imgData != False:
                dataWriter.writerow(imgData)
                successCount += 1
            else:
                errorCount += 1

    # Calculate the error rate
    errorRate = float(errorCount) / (errorCount + successCount)

    # Close the data file
    dataFile.close()

    return errorRate
    

if __name__ == '__main__':
    import sys

    videoPath = sys.argv[1]

    print("Generating screencaptures . . .", end='\n\n')

    if not generateScreenCaps(videoPath, 10000):       # exit if something went amiss
        print("Exiting script . . . ")
        sys.exit(0)
    
    print("Finished generating screencaptures", end='\n\n')

    print("Writing to csv . . . ", end='\n\n')

    errorRate = writeScreenCapData()

    print("Finished writing to csv with an error rate of " + str(errorRate))
