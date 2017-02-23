#!/usr/bin/python

# A more complex RGBMatrix example works with the Python Imaging Library,
# demonstrating a few graphics primitives and image loading.
# Note that PIL graphics do not have an immediate effect on the display --
# image is drawn into a separate buffer, which is then copied to the matrix
# using the SetImage() function (see examples below).
# Requires rgbmatrix.so present in the same directory.

# PIL Image module (create or load images) is explained here:
# http://effbot.org/imagingbook/image.htm
# PIL ImageDraw module (draw shapes to images) explained here:
# http://effbot.org/imagingbook/imagedraw.htm

import Image
import ImageDraw
import requests
import hashlib
import time
from io import BytesIO
from rgbmatrix import Adafruit_RGBmatrix

# Requests the avatar image
email = "cristobal23@gmail.com"
size = 32
gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest()
r = requests.get(gravatar_url)

# Creates the avatar image
avatar = Image.open(BytesIO(r.content))
avatar.load()
small_avatar = avatar.resize((size,size), Image.ANTIALIAS)

# Creates the text field
text = Image.new("RGB", (60, 32))
context = ImageDraw.Draw(text)
context.text((0,0), "Whistle", fill=(0,200,0))
context.text((0,10), "Hackweek", fill=(0,0,200))
context.text((0,20), "2017 !!!", fill=(0,200,200))

# Combines the avatar image with the text field
image = Image.new("RGB", (90, 32))
image.paste(small_avatar, (0,0))
image.paste(text, (40,0))

# Rows and chain length are both required parameters:
matrix = Adafruit_RGBmatrix(32, 2)

matrix.Fill(0x6F85FF)
# 24-bit RGB scrolling example.
while True:
        matrix.Clear()
        for n in range(64, -image.size[0], -1):
	        matrix.SetImage(image.im.id, n, 0)
	        time.sleep(0.025)

matrix.Clear()
