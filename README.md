A Python3 script to read data from https://www.youtube.com/watch?v=raiFrxbHxV0.

When run with no optional arguments, this writes data to a csv file 'data.csv' in the current working directory; video frames are saved in './frames' in uncompressed bmp format. Also, check to make sure that the default time offset () corresponds to the 00:00.000 clock time in the video frame for your file; if not pass it in with --timeoffset.

Because of compression in the Youtube video, and also due to imperfections in Tesseract OCR, some data points become corrupted and are not included in the output csv. A consequence of this is that the time intervals between points will not in general be uniform.

The time values should be valid to within about 70ms. Some of these data points will be misread if Tesseract OCR mistakes one digit for another, so make sure to give the output csv a once-over before using the data.

--

Run this on the command line with

```
python3 redBullFetch.py path_to_video
```
and display optional arguments with 

```
python3 redBullFetch.py --help
```

You can download the video with youtube-dl using default settings (HQ) like so:

```
youtube-dl https://www.youtube.com/watch?v=raiFrxbHxV0
```

Works on Linux, probably on Mac, and definitely not on Windows.

--

Dependencies:

Python 3 - https://www.python.org/

FFmpeg - https://ffmpeg.org/

tesserocr - https://pypi.python.org/pypi/tesserocr

Pillow - https://pypi.python.org/pypi/Pillow/4.0.0

--

Possible improvements:

1. Train Tesseract OCR. I have no idea how to do this, but from the little research I did it looks complicated.
2. Blacklist all non-numeric characters and whitelist numeric characters. This is actually easy, but see the (*) below
3. Process the images better. I spent about two hours trying this before giving up in frustration. I'm sure someone who knows what they're doing can make *huge* improvements to my error rate by touching up the image properly, but my attempts led to minimal improvement.
4. Add parallel processing support. A bit of work, but this is processing-heavy enough to warrant it.
5. Extend error detection by comparing data-points with their neighbours. Currently error detection is only done for points in isolation.

[*] (1) (1) and (2) above would require using the tesserocr.PyTessAPI class to read images, rather than the convenient tesserocr.image_to_text function.
