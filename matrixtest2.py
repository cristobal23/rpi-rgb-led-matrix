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
from HTMLParser import HTMLParser
import feedparser
import syslog
import os
import sys


syslog.syslog('Starting application')

if 'JIRA_USERNAME' not in os.environ:
    syslog.syslog(syslog.LOG_ERR, 'JIRA_USERNAME is not defined')
    sys.exit(2)

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def create_image():
    syslog.syslog('Creating new image')
    username = os.environ.get('JIRA_USERNAME')
    password = os.environ.get('JIRA_PASSWORD')
    d = feedparser.parse('https://' + username + ':' + password + '@whistle.atlassian.net/activity')
    avatar_url = d.entries[0].links[1].href
    size = 32

    # Create the avatar image
    avatar_string = u'avatarId'
    if avatar_string in avatar_url:
        small_avatar = Image.open("jira.png")
        small_avatar.load()
        msg = u'Tried to load an avatar from ' + avatar_url
        syslog.syslog(msg)
    else:
        r = requests.get(avatar_url, auth=(username, password))
        avatar = Image.open(BytesIO(r.content))
        avatar.load()
        small_avatar = avatar.resize((size,size), Image.ANTIALIAS)

    # Parse the entry
    top_row = d.entries[0].authors[0].name
    middle_row = strip_tags(d.entries[0].title).split()[2] + ' ' + strip_tags(d.entries[0].title).split()[3]
    last_row = " ".join(strip_tags(d.entries[0].title).split()[4:])

    # Create the text field
    text = Image.new("RGB", (128, 32))
    context = ImageDraw.Draw(text)
    context.text((0,0), top_row, fill=(0,200,0))
    context.text((0,10), middle_row, fill=(0,0,200))
    context.text((0,20), last_row, fill=(0,200,200))

    # Combine the avatar image with the text field
    image = Image.new("RGB", (160, 32))
    image.paste(small_avatar, (0,0))
    image.paste(text, (40,0))

    return image

# Rows and chain length are both required parameters:
matrix = Adafruit_RGBmatrix(32, 2)

matrix.Fill(0x6F85FF)
# 24-bit RGB scrolling example.
while True:
    matrix.Clear()
    image = create_image()
    for n in range(64, -image.size[0], -1):
        matrix.SetImage(image.im.id, n, 0)
        time.sleep(0.025)

matrix.Clear()
