#!/usr/bin/python3

import os
import subprocess
import re
import csv
import argparse
from PIL import Image
from tesserocr import image_to_text

def generateFrames(videoPath, fps, outType, frameDir,
                    verbose=False, quiet=False):
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
    verbose - option to give more output
    quiet - optoin to give less output
    '''

    # Check if save directory exists; create it if not
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    # Check if save directory is empty; if it isn't
    # prompt to use existing files or exit script
    if os.listdir(frameDir):
        print(frameDir + ' is not empty!', end='\n\n')
        print('Use existing files? (exit otherwise)')
        if input('(Y/N) > ').lower() in {'yes', 'y', 'ye', ''}:
            return
        else:
            raise OSError('Need an empty directory to generate frames!')

    # Set how noisy ffmpeg should be
    if verbose:
        loglevel = 'verbose'
    elif quiet:
        loglevel = 'fatal'
    else:
        loglevel = 'info'

    # Generate video frames using ffmpeg
    # Reference: https://ffmpeg.org/ffmpeg-filters.html#fps
    subprocess.run(['ffmpeg', '-loglevel', loglevel,
        '-i', videoPath, '-vf', 'fps=' + str(fps),
        frameDir + '/img%06d.'+outType.lower()])

    return


def processFrame(frameImage):
    '''
    Extract text from a PIL image frame
    '''

    # Extract subset of image corresponding to data
    timeImage = frameImage.crop((589,656,751,701))
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

    timeImage = timeImage.convert('L')
    timeImage = timeImage.point(lambda x: 0 if x<220 else 255, '1')
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
    time = image_to_text(timeImage, psm=6)
    altitude = image_to_text(altitudeImage, psm=6)
    speed = image_to_text(speedImage, psm=6)
    heart = image_to_text(heartImage, psm=6)
    respir = image_to_text(respirImage, psm=6)
#    vertG = image_to_text(vertGImage)
#    latG = image_to_text(latGImage)
#    longG = image_to_text(longGImage)

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
        timeReal = (float(matchTime.group('mins')) * 60
                + float(matchTime.group('secs'))
                + float(matchTime.group('msecs')) * 1e-3)

        # In the video time is negative before the jump
        if matchTime.group('sign') == '-':
                timeReal *= -1

        return (timeReal, altitude, speed, heart, respir)

    except AttributeError:
        # Such error! OCR failed!
        return False


def writeFrameData(dataPath, frameDir, verbose=False, quiet=False):
    '''
    Write frame data to csv file.

    Arguments:
    dataPath - relative path to data file
    frameDir - relative path to directory containing
                frames
    verbose - option to give more output
    quiet - option to give less output
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

    # Process each frame
    errorCount = 0
    successCount = 0
    for frame in frameList:
        with Image.open(frameDir + '/' + frame) as frameImage:
            if verbose:
                print('Processing ' + frame)

            frameData = processFrame(frameImage)

            if frameData != False:
                dataWriter.writerow(frameData)
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
    parser.add_argument("--verbose",
            help="Option to give more detailed output",
            action="store_true")
    parser.add_argument("--quiet",
            help="Option to give less ouput",
            action="store_true")
    args = parser.parse_args()

    # Correct possible oversampling
    if args.fps > 29.97:
        if not args.quiet:
            print("Correcting oversampling . . .")
            print("Sampling changed to 29.97fps (maximum)", end='\n\n')
        args.fps = 29.97

    # Generate frames
    if not args.quiet:
        print("Getting video frames . . .", end='\n\n')

    try:
        generateFrames(args.vidFile, args.fps, args.frameext, args.framedir,
                            args.verbose, args.quiet)
    except OSError:
        if not args.quiet:
            print("Exiting script . . .")
        sys.exit(1)

    if not args.quiet:
        print("Finished getting video frames", end='\n\n')

    # Write to data file
    if not args.quiet:
        print("Writing to %s . . ." % (args.output), end='\n\n')

    errorRate = writeFrameData(args.output, args.framedir,
                                 args.verbose, args.quiet)

    if not args.quiet:
        print(("Finished writing data with an error rate of (at least) "
            + str(errorRate)))
