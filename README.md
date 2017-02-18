A Python3 script to read data from https://www.youtube.com/watch?v=raiFrxbHxV0
Writes to a csv file data.csv in the cwd by default
(if data.csv already exists, it will prompt for another file path)

Use:

```
python3 redBullFetch.py videoname
```

I used youtube-dl to download the above video with default settings (HQ), but this
might still work if you downloaded the video differently.

Works on Linux, probably on Mac, and definitely not on Windows.

Dependencies:

tesserocr - https://pypi.python.org/pypi/tesserocr
Pillow	  - https://pypi.python.org/pypi/Pillow/4.0.0
