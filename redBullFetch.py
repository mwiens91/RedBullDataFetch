import os
import subprocess
import re
import csv
from PIL import Image
from tesserocr import image_to_text

def generateScreenCaps(avFile, fps=3,
                        screenDir=os.getcwd() + '/screens'):
    '''
    Generate screen captures from a video file using an FFmpeg call
    on the command line

    Arguments:
    avFile - relative path to video file
    fps - number of frames to capture per second
            default is 15 if left out
    screenDir - relative path to screencapture directory
            Default is ./screens
    '''

    # Check if save directory exists; create it if not
    if not os.path.exists(screenDir):
        os.makedirs(screenDir)

    # Check if save directory is empty; if it isn't
    # prompt to use existing files or exit script
    if os.listdir(screenDir):
        print(screenDir + ' is not empty!', end='\n\n')
        print('Use existing files? (exit otherwise)')
        if input('(Y/N) > ').lower() in {'yes', 'y', 'ye', ''}:
            print()
            return
        else:
            print()
            raise OSError('Need an empty directory to generate screencaps!')

    # Generate screencaptures using ffmpeg
    subprocess.run(['ffmpeg', '-i', './' + avFile, '-vf', 'fps=' + fps,
        screenDir + '/img%08d.bmp'])

    return


def processScreenCap(screenCaptureObj):
    '''
    Extract text from a screencapture PIL image object
    '''

    # Extract subset of image corresponding to data
    timeImg = screenCaptureObj.crop((589,656,751,701))
#    vertGImg = screenCaptureObj.crop((595,731,642,751))
#    latGImg = screenCaptureObj.crop((595,751,635,772))
#    longGImg = screenCaptureObj.crop((596,771,639,792))
    altitudeImg = screenCaptureObj.crop((1359,226,1464,254))    # in m
    speedImg = screenCaptureObj.crop((1665,226,1764,256))       # in kph 
    heartImg = screenCaptureObj.crop((1368,526,1460,555))       # in bpm
    respirImg = screenCaptureObj.crop((1356,565,1463,594))      # respiration
                                                                # in ???

    # Process images for more accurate OCR readings
    # The time has a semitransparent moving background,
    # making text recognition difficult
    #
    # I've kind of haphazardly determined that these settings
    # result in an improvement of text recognition, but doubtless
    # there are better modifications
    timeImg = timeImg.convert('L')
    timeImg = timeImg.point(lambda x: 0 if x<220 else 255, '1') 
#    vertGImg = vertGImg.convert('L')
#    vertGImg = vertGImg.point(lambda x: 0 if x<220 else 255, '1') 
#    latGImg = latGImg.convert('L')
#    latGImg = latGImg.point(lambda x: 0 if x<220 else 255, '1') 
#    longGImg = longGImg.convert('L')
#    longGImg = longGImg.point(lambda x: 0 if x<220 else 255, '1') 

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
#    vertG = image_to_text(vertGImg)
#    latG = image_to_text(latGImg)
#    longG = image_to_text(longGImg)

    # Strip trailing whitespace Tesseract OCR seems to pick up 
    time = time.rstrip()
    altitude = altitude.rstrip()
    speed = speed.rstrip()
    heart = heart.rstrip()
    respir = respir.rstrip()
#    vertG = vertG.rstrip()
#    latG = latG.rstrip()
#    longG = longG.rstrip()

    # Split time string into components
    matchTime = re.match(
        r'^(?P<sign>-?)(?P<mins>\d+):(?P<secs>\d+)\.(?P<msecs>\d+)$', time)

    # Return the data points if everything is okay. Otherwise
    # return false
    try:
        # A number of sanity checks follow. Sometimes
        # errors sneak in, so it's good to overly cautious here
        # Choose which conditions you like (or add more), depending
        # on what errors you want to allow.
        if (
            len(heart) != 3 or                  # heart rate is 3 digits
            len(respir) != 2 or                 # respiration is 2 digits
            len(speed) == 0 or                  # speed is not 0 digits
            len(matchTime.group('mins')) != 2 or    # Next 3 lines:
            len(matchTime.group('secs')) != 2 or    # time not corrupted
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
    '''
    Write data to a csv file. A "parent" function.

    Arguments:
    screenDir - relative path to screencapture directory
            Default is ./screens
    dataSheetFile - relative path to csv datasheet
            Defailt is ./data.csv
    '''

    # Open a datasheet
    # If the file given in the argument dataSheetFile exists,
    # prompt for a new file path until there isn't a conflict.
    while os.path.isfile(dataSheetFile):
        print(dataSheetFile + " already exists!")
        print("Enter the relative path for the datasheet:")
        dataSheetFile = input("> ")
        print()

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

    print("Getting screencaptures . . .", end='\n\n')

    try:
        # Second argument is the number of frames you want to capture
        # per second of video
        generateScreenCaps(videoPath, 1)
    except OSError:
        print("Exiting script . . . ")
        sys.exit(1)
    
    print("Finished getting screencaptures", end='\n\n')

    print("Writing to csv . . . ", end='\n\n')

    errorRate = writeScreenCapData()

    print("Finished writing to csv with an error rate of " + str(errorRate))
