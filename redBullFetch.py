#!/usr/bin/python3

import os
import subprocess
import re
import csv
import argparse
from PIL import Image
from tesserocr import image_to_text

def generateFrames(videoPath, fps, outType, frameDir):
    '''
    Generate frames from a video file using an FFmpeg call
    on the command line

    Arguments:
    videoPath - relative path to video file
    fps - number of frames to capture per second
    outType - The output type of each frame. BMP is uncompressed so is fast to
            extract, but will take up considerable disk space. JPEG and PNG are
            compressed options that are lossey/loss-less and moderate/slow
            respectively.
    frameDir - relative path to video frame save directory
    '''

    # Check if save directory exists; create it if not
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    # Check if save directory is empty; if it isn't
    # prompt to use existing files or exit script
    if os.listdir(frameDir):
        print(frameDir + ' is not empty!', end='\n\n')
        print('Use existing files? (assuming fps=%f)' % fps)
        if input('(Y/N) > ').lower() in {'yes', 'y', 'ye', ''}:
            return
        else:
            raise OSError('Need an empty directory to generate frames!')

    # Generate video frames using ffmpeg
    # Reference: https://ffmpeg.org/ffmpeg-filters.html#fps
    subprocess.run(['ffmpeg', '-i', videoPath, '-vf', 'fps=' + str(fps),
        frameDir + '/img%06d' + '_fps_' + str(fps) + '.' + outType.lower()])

    return


def processFrame(frameImage):
    '''
    Extract text from a PIL image frame.
    Lots of commented out code, depending on
    what you want to read using the OCR.
    '''

    # Extract subset of image corresponding to data
#    timeImage = frameImage.crop((589,656,751,701))
#    vertGImage = frameImage.crop((595,731,642,751))
#    latGImage = frameImage.crop((595,751,635,772))
#    longGImage = frameImage.crop((596,771,639,792))
    altitudeImage = frameImage.crop((1359,226,1464,254))    # in m
    speedImage = frameImage.crop((1665,226,1764,256))       # in kph
    heartImage = frameImage.crop((1368,526,1460,555))       # in bpm
    respirImage = frameImage.crop((1356,565,1463,594))      # respiration
                                                            # in ???

    # Process images for more accurate OCR readings
    # - convert('L') makes the image greyscale
    # - the inline function forces pixels either black
    #   or white

#    timeImage = timeImage.convert('L')
#    timeImage = timeImage.point(lambda x: 0 if x<220 else 255, '1')
#    vertGImage = vertGImage.convert('L')
#    vertGImage = vertGImage.point(lambda x: 0 if x<220 else 255, '1')
#    latGImage = latGImage.convert('L')
#    latGImage = latGImage.point(lambda x: 0 if x<220 else 255, '1')
#    longGImage = longGImage.convert('L')
#    longGImage = longGImage.point(lambda x: 0 if x<220 else 255, '1')

    altitudeImage = altitudeImage.convert('L')
    speedImage = speedImage.convert('L')
    heartImage = heartImage.convert('L')
    respirImage = respirImage.convert('L')

    # Extract text from images using Tesseract OCR
    # Page Segmentation Method 6 says
    # "Assume a single uniform block of text."
#    time = image_to_text(timeImage, psm=6)
    altitude = image_to_text(altitudeImage, psm=6)
    speed = image_to_text(speedImage, psm=6)
    heart = image_to_text(heartImage, psm=6)
    respir = image_to_text(respirImage, psm=6)
#    vertG = image_to_text(vertGImage)
#    latG = image_to_text(latGImage)
#    longG = image_to_text(longGImage)

    # Strip trailing whitespace Tesseract OCR seems to pick up
#    time = time.rstrip()
    altitude = altitude.rstrip()
    speed = speed.rstrip()
    heart = heart.rstrip()
    respir = respir.rstrip()
#    vertG = vertG.rstrip()
#    latG = latG.rstrip()
#    longG = longG.rstrip()

    # Split time string into components
#    matchTime = re.match(
#        r'^(?P<sign>-?)(?P<mins>\d+):(?P<secs>\d+)\.(?P<msecs>\d+)$', time)

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
            len(speed) == 0                     # speed is not 0 digits
#            len(matchTime.group('mins')) != 2 or    # Next 3 lines:
#            len(matchTime.group('secs')) != 2 or    # time not corrupted
#            len(matchTime.group('msecs')) != 3
            ):
            raise AttributeError('Bad data')

        # Convert time components into seconds
#        timeReal = (float(matchTime.group('mins')) * 60
#                + float(matchTime.group('secs'))
#                + float(matchTime.group('msecs')) * 1e-3)

        # In the video time is negative before the jump
#        if matchTime.group('sign') == '-':
#                timeReal *= -1

        return [altitude, speed, heart, respir]

    except AttributeError:
        # Such error! OCR failed!
        return False


def writeFrameData(fps, timeOffset, dataPath, frameDir, verbose=False):
    '''
    Write frame data to csv file.

    Arguments:
    fps - number of frames captured per seconds
    timeOffset - Time in video (in s) corresponding
                to frame clock time 00:00.000
    dataPath - relative path to data file
    frameDir - relative path to directory containing
                frames
    verbose - flag controlling whether to give lots of
                output to stdout. Default is off.
    '''

    # Open the data file
    # If the data file already exists, prompt for a new file
    # path until there isn't a conflict.
    while os.path.isfile(dataPath):
        print(dataPath + " already exists!")
        print("Enter the relative path for the datasheet:")
        dataPath = input("> ")
        print()

    dataFile = open(dataPath, 'w')
    dataWriter = csv.writer(dataFile)

    # Write headings to the data sheet
    dataWriter.writerow(('Time (s)', 'Altitude (m)', 'Speed (kph)',
        'Heart rate (bpm)', 'Respiration (???)'))

    # Get all video frame filenames
    frameList = os.listdir(frameDir)
    frameList.sort()

    # Determine time interval between frames
    timeSep = 1 / fps

    # Process each frame 
    # Couple of starting variables
    errorCount = 0
    successCount = 0
    frameTime = -timeOffset + 1/fps / 2     # see http://bit.ly/2loKRZh

    for frame in frameList:
        with Image.open(frameDir + '/' + frame) as frameImage:
            if verbose:
                print('Processing ' + frame)

            # Pull data off the frame with OCR
            frameData = processFrame(frameImage)

            if frameData != False:
                fullData = [frameTime]
                fullData += frameData
                dataWriter.writerow(fullData)
                successCount += 1
            else:
                errorCount += 1

            # Set the time for the next iteration
            frameTime += timeSep

    # Calculate the error rate
    errorRate = float(errorCount) / (errorCount + successCount)

    # Close the data file
    dataFile.close()

    return errorRate


if __name__ == '__main__':
    import sys

    # Parse input arguments for video file, fps, output frame format, etc.
    parser = argparse.ArgumentParser()
    parser.add_argument("vidFile", help="Path to video file", type=str)
    parser.add_argument("-o", "--output", type=str, default='./data.csv',
            help="Path to output csv datafile")
    parser.add_argument("-f", "--fps", type=float, default=3,
            help="Number of frames to analyse per second")
    parser.add_argument("-e", "--frameext", type=str, default='bmp',
            help="Output frame format. BMP, JPEG, and PNG are good choices.")
    parser.add_argument("-d", "--framedir", type=str, default='./frames',
            help="Directory to save video frames")
    parser.add_argument("--timeoffset", type=float, default=7.75,
        help="Time in video (in s) corresponding to frame clock time 00:00.000")
    parser.add_argument("--verbose",
            help="Option to give more detailed output",
            action="store_true")
    args = parser.parse_args()

    # Correct possible oversampling
    if args.fps > 29.97:
        print("Correcting oversampling . . .")
        print("Sampling changed to 29.97fps (maximum)", end='\n\n')
        args.fps = 29.97

    # Generate frames
    print("Getting video frames . . .", end='\n\n')

    try:
        generateFrames(args.vidFile, args.fps, args.frameext, args.framedir)
    except OSError:
        print("Exiting script . . .")
        sys.exit(1)

    print("Finished getting video frames", end='\n\n')

    # Write to data file
    print("Writing to %s . . ." % (args.output), end='\n\n')

    errorRate = writeFrameData(args.fps, args.timeoffset, args.output,
                    args.framedir, args.verbose)

    print(("Finished writing data with an error rate of (at least) "
        + str(errorRate)))
