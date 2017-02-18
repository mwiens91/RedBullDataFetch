A Python3 script to read data from https://www.youtube.com/watch?v=raiFrxbHxV0.

Writes to a csv file data.csv located in the current working directory by default; if data.csv already exists, it will prompt for another file path.

Because of compression in the Youtube video, and also due to imperfections in Tesseract OCR, some data points become corrupted and are not included in the output csv. A consequence of this is that the time intervals between points will not in general be uniform.

The error rate is about 35% (yikes!). Since the video has ~17,000 frames, this means that you can expect about 11,000 frames as an upper limit.

Run this on the command line with

```
python3 redBullFetch.py videoname
```
and set the time interval between screencaptures (in ms) using the second argument of

```python
if not generateScreenCaps(videoPath, 10000): 
```

at ~line 160 of the python script.

I used youtube-dl to download the above video with default settings (HQ), but this might still work if you downloaded the video differently.

Works on Linux, probably on Mac, and definitely not on Windows.

Dependencies:

Python 3 - https://www.python.org/

FFmpeg - https://ffmpeg.org/

tesserocr - https://pypi.python.org/pypi/tesserocr

Pillow	  - https://pypi.python.org/pypi/Pillow/4.0.0

--

Possible improvements:

1. Train Tesseract OCR. I have no idea how to do this, but from the little research I did it looks complicated.
2. Process the images better. I spent about two hours trying this before giving up in frustration. I'm sure someone who knows what they're doing can make *huge* improvements to my error rate by touching up the image properly, but my attempts led to minimal improvement.
3. Calculate time instead of grabbing the time from the screencaptures. Instead of using OCR to read the time text off the video—which has proved to be quite problematic—I could, knowing where I start taking screencaptures, knowing the time interval between screencaptures, and knowing the scale of time in the video ((how many seconds elapse in the time text of the video):(how many seconds elapsed in the video)—probably 1:1, but I wouldn't be shocked if it wasn't), I could just calculate the time a screencapture corresponds to—far more reliable than using Tesseract OCR to try and scan it. 
