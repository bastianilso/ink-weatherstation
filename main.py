#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
assetsdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
screendir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen')
bmpdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bmp-out')
if os.path.exists(libdir):
    sys.path.append(libdir)

filename_template = 'screen_template'
filename_out = 'screen_current'
    
from lxml import etree
                                         
from lib.weather import WeatherUpdate
from lib.calendar import CalendarUpdate
from lib.slideshow import SlideshowUpdate


svg_template = os.path.join(screendir, filename_template + '.svg')
svg_out = os.path.join(screendir, filename_out + '.svg')
ns = {'s': 'http://www.w3.org/2000/svg'}

tree = etree.parse(open(svg_template))

slideshow_id = 'slideshow-plants'

WeatherUpdate(tree)
SlideshowUpdate(tree, assetsdir, slideshow_id)
CalendarUpdate(tree)


with open(svg_out, "wb") as o:
    o.write(etree.tostring(tree, pretty_print=True))

#print(os.path.join(screendir, filename_out))
# Inkscape 0.9.x Flatpak
os.system("flatpak run --command=\'inkscape\' org.inkscape.Inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page -e " + os.path.join(screendir, filename_out + '.png'))

# Inkscape 0.9.x
#os.system("inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page -e " + os.path.join(screendir, filename_out + '.png'))
# Inkscape 1.0
#os.system("inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page --export-filename " + os.path.join(screendir, filename_out + '.png'))
#os.system("convert " + os.path.join(screendir, filename_out + '.png') + " -rotate 90 " + os.path.join(bmpdir, filename_out + '.bmp'))
# Transfer to e-ink screen
#os.system("sudo ./epd -2.30")

