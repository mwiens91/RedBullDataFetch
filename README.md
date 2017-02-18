A Python3 script to read data from https://www.youtube.com/watch?v=raiFrxbHxV0.

Writes to a csv file data.csv located in the current working directory by default; if data.csv already exists, it will prompt for another file path.

Because of compression in the Youtube video, and also due to imperfections in Tesseract OCR, some data points become corrupted and are not included in the output csv. A consequence of this is that the time intervals between points will not in general be uniform.

The error rate is about 50% (yikes!). This isn't quite so bad considering that the video time count has about 540000ms. This means that at most we can expect to get around 270,000 data points, which is not so bad for many purposes.

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

tesserocr - https://pypi.python.org/pypi/tesserocr

Pillow	  - https://pypi.python.org/pypi/Pillow/4.0.0
