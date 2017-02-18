A Python3 script to read data from https://www.youtube.com/watch?v=raiFrxbHxV0.
Writes to a csv file data.csv in the cwd by default
(if data.csv already exists, it will prompt for another file path)

Because of compression in the Youtube video, and also due to imperfections in Tesseract OCR, some data points are left out, so time intervals between points in general will not be uniform. The error rate is about <error rate here>.

Run this on the command line with

```
python3 redBullFetch.py videoname
```

I used youtube-dl to download the above video with default settings (HQ), but this
might still work if you downloaded the video differently.

Works on Linux, probably on Mac, and definitely not on Windows.

Dependencies:

tesserocr - https://pypi.python.org/pypi/tesserocr
Pillow	  - https://pypi.python.org/pypi/Pillow/4.0.0
