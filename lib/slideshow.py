#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
from datetime import date, timedelta
import os

ns = {'s': 'http://www.w3.org/2000/svg'}
xlink = '{http://www.w3.org/1999/xlink}'

def GetNth(text):
    year = date.today().year
    n = text[year % len(text)]
    return n

# Slideshow viewer
# Fetch all assets into a dictionary, with text, images, source
def SlideshowUpdate(tree, assetsdir, slideshow_id):
    included_extensions = ['-image.png']
    file_names = [fn for fn in os.listdir(os.path.join(assetsdir, slideshow_id))
                  if any(fn.endswith(ext) for ext in included_extensions)]
    file_names = [ fn.replace('-image.png','') for fn in file_names ]
    file_names2 = [ fn.replace('-text.png','') for fn in file_names ]
    week_number = date.today().isocalendar()[1]
    file_names = sorted(file_names, key=GetNth)
    chosen = file_names[week_number % len(file_names)]
    
    slide_image = tree.xpath("//s:image[@id='slide-image']", namespaces=ns)[0]
    slide_text = tree.xpath("//s:image[@id='slide-text']", namespaces=ns)[0]

    slide_image.attrib[xlink+'href'] = '../assets/' + slideshow_id + '/' + chosen + '-image.png'
    slide_text.attrib[xlink+'href'] = '../assets/' + slideshow_id + '/' + chosen + '-text.png'
    
    print(slide_image.attrib[xlink+'href'])
    print(slide_text.attrib[xlink+'href'])
