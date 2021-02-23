#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import requests
from lxml import etree

ns = {'s': 'http://www.w3.org/2000/svg'}

def ChooseWeatherIcon(tree, weather, icons, namespace):
    print(icons)
    chosen_icon = "none"
    if (weather in ["lightrain","cloudy","fog"]):
        chosen_icon = namespace + "-" + "cloud"
    elif (weather in ["rain","heavyrain"]):
        chosen_icon = namespace + "-" + "rainy"
    elif (weather in ["partlycloudy_day","partlycloudy_night"]):
        chosen_icon = namespace + "-" + "suncloudy"
    elif (weather in ["fair_night","clearsky_night","fair_day","clearsky_day"]):
        chosen_icon = namespace + "-" + "sun"
    elif (weather in ["snow","snowy"]):
        chosen_icon = namespace + "-" + "snowy"
    print(chosen_icon)
    for icon in icons:
        if (icon != chosen_icon):
            path = "//s:g[@id='" + icon + "']"
            to_remove = tree.xpath(path, namespaces=ns)[0]
            p = to_remove.getparent()
            p.remove(to_remove)

def SetTemperature(tree, temperature, identifier):
  root = tree.getroot()
  for elem in root.getiterator():
      try:
          elem.text = elem.text.replace(identifier, temperature +"\N{DEGREE SIGN}")
      except AttributeError:
          pass


def WeatherUpdate(tree):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    url ="https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=57.0488&lon=9.9217"
    response = requests.get(url, headers = user_agent)
    data = json.loads(response.text)
    
    for i in range(1,10):
        w_ns = "w" + str(i)
        icons_available = [w_ns + "-suncloudy",w_ns + "-sun",w_ns + "-cloud",w_ns + "-rainy",w_ns + "-snowy"]
        icon_now = data['properties']['timeseries'][i]['data']['next_1_hours']['summary']['symbol_code']
        ChooseWeatherIcon(tree, icon_now, icons_available, w_ns)
        t_id = "$t" + str(i)
        temp_now = data['properties']['timeseries'][i]['data']['instant']['details']['air_temperature']
        SetTemperature(tree, str(round(temp_now)), t_id)
	
