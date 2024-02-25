#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import traceback
import os
import logging
from logging.handlers import RotatingFileHandler
import locale



######################
# Setup Logging System
######################
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
log_file = 'inkscreen.log'
my_handler = RotatingFileHandler(log_file, mode='a', maxBytes=1024*1024*5,
backupCount=1,encoding=None,delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(my_handler)

######################
# Setup directories
######################
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

logger.debug(assetsdir)
logger.debug(libdir)
logger.debug(screendir)
logger.debug(bmpdir)
logger.debug(svg_template)
logger.debug(svg_out)

######################
# Code Logic
######################

def update_screen():
    tree = etree.parse(open(svg_template))


    slideshow_id = 'slideshow-plants'

    # set locale to danish while creating content
    sys_locale = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
    WeatherUpdate(tree)
    SlideshowUpdate(tree, assetsdir, slideshow_id)
    CalendarUpdate(tree)
    
    # set locale back to system for export, to avoid converting ø to weird characters. 
    locale.setlocale(locale.LC_ALL, sys_locale)

    with open(svg_out, "wb") as o:
        o.write(etree.tostring(tree, pretty_print=True))

    #print(os.path.join(screendir, filename_out))
    # Inkscape 0.9.x Flatpak
    #os.system("flatpak run --command=\'inkscape\' org.inkscape.Inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page -e " + os.path.join(screendir, filename_out + '.png'))

    # Inkscape 0.9.x
    os.system("inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page -e " + os.path.join(screendir, filename_out + '.png'))
    # Inkscape 1.0
    #os.system("inkscape -w 1404 -h 1872 " + os.path.join(screendir, filename_out + '.svg') + " --export-area-page --export-filename " + os.path.join(screendir, filename_out + '.png'))
    os.system("convert " + os.path.join(screendir, filename_out + '.png') + " -rotate 270 -flip " + os.path.join(bmpdir, filename_out + '.bmp'))
    # Transfer to e-ink screen
    os.system("cd /home/dietpi/IT8951-ePaper/Raspberry/ && sudo ./epd -2.30 1")

######################
# Execution
######################

try:
    update_screen()
    logger.debug('Screen updated without errors.')
except:
    logger.error(traceback.format_exc())
    # should we clear screen in case of error?
    #os.system("cd /home/dietpi/IT8951-ePaper/Raspberry/ && sudo ./epd_reset -2.30 1")
