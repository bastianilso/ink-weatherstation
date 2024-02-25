#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import requests
from datetime import date, datetime
from suntime import Sun
import calendar
from lxml import etree

ns = {'s': 'http://www.w3.org/2000/svg'}

w_names =  {'clear': "clear sky",
'cloudy': "cloudy",
'fair': "fair weather",
'fog': "foggy",
'heavyrain': "heavy rain",
'heavysleet': "heavy sleet",
'heavysnow': "heavy snow",
'lightrain': "light rain",
'lightsleet': "light sleet",
'lightsnow': "light snow",
'partlycloudy': "partly cloudy",
'heavyrainshower': "heavy rain shower",
'heavysleet': "heavy sleet",
'rain': "rainy",
'sleet': "sleety",
'snow': "snowy" }

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

def SetText(tree, identifier, value):
  root = tree.getroot()
  for elem in root.getiterator():
      try:
          elem.text = elem.text.replace(identifier, value)
      except AttributeError:
          pass

def WeatherUpdate(tree):
    #user_agent = {'User-agent': 'Mozilla/5.0'}
    user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url ="https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=57.0488&lon=9.9217"
    response = requests.get(url, headers = user_agent)
    #print(response.text).weekday()
    data = json.loads(response.text)
    
    weekdayindexes = [1]
    tm = len(data['properties']['timeseries'])
    for i in range(1,tm):
        weekday = -1
        c_date = datetime.strptime(data['properties']['timeseries'][i]['time'], "%Y-%m-%dT%H:%M:%SZ")
        if (c_date.strftime("%d") == date.today().strftime("%d")):
            continue
        if (c_date.weekday() > weekday):
            weekday = c_date.weekday()
            if (c_date.hour == 18):
                weekdayindexes.append(i)
        if len(weekdayindexes) > 6: # limit description to six days forward.
            break
    
    textstring = ""
    
    for i in weekdayindexes:
        if ('next_6_hours' in data['properties']['timeseries'][i]['data']):
            icon_now = data['properties']['timeseries'][i]['data']['next_6_hours']['summary']['symbol_code']
            weather_name = "happy day"
            for key in w_names:
                if (icon_now.startswith(key)):
                    weather_name = w_names[key]
        
        c_date = datetime.strptime(data['properties']['timeseries'][i]['time'],"%Y-%m-%dT%H:%M:%SZ")
        textstring += calendar.day_name[c_date.weekday()]
        textstring += " "
        textstring += weather_name
        textstring += " with "
        textstring += str(data['properties']['timeseries'][i]['data']['instant']['details']['wind_speed'])
        textstring += " "
        textstring += data['properties']['meta']['units']['wind_speed']
        textstring += ". "
    # Add string describing latest update.
    textstring += "Updated on "
    textstring += datetime.now().strftime("%d/%m %H:%M")
    textstring += ". "
    print(textstring)
        
    SetText(tree, "$wd", textstring)
    
    wind_val = str(data['properties']['timeseries'][1]['data']['instant']['details']['wind_speed']) + data['properties']['meta']['units']['wind_speed']
    print(wind_val)
    SetText(tree, "$wind", wind_val)
    
    rain_val = str(data['properties']['timeseries'][1]['data']['next_6_hours']['details']['precipitation_amount']) + data['properties']['meta']['units']['precipitation_amount']
    SetText(tree, "$rain", rain_val)
    
    sun = Sun(57.0488, 9.9217)
    sun_val = sun.get_sunset_time().strftime("%H:%M")
    print(sun_val)
    SetText(tree, "$sun", sun_val)
    
    for i in range(1,9):
        # set weather icon
        w_ns = "w" + str(i)
        icons_available = [w_ns + "-suncloudy",w_ns + "-sun",w_ns + "-cloud",w_ns + "-rainy",w_ns + "-snowy"]
        icon_now = data['properties']['timeseries'][i]['data']['next_1_hours']['summary']['symbol_code']
        ChooseWeatherIcon(tree, icon_now, icons_available, w_ns)
        # set wind speed
        # set 3-letter weekday
        d_id = "$d" + str(i)
        if d_id == "$d1":
            d_val = calendar.day_name[date.today().weekday()] + " " + date.today().strftime("%d/%m")
            SetText(tree, d_id, d_val)
        else:
            c_date = datetime.strptime(data['properties']['timeseries'][i]['time'],"%Y-%m-%dT%H:%M:%SZ")
            d_val = c_date.strftime("%H:%M")
            SetText(tree, d_id, d_val)
        # set temperature
        t_id = "$t" + str(i)
        temp_now = data['properties']['timeseries'][i]['data']['instant']['details']['air_temperature']
        SetText(tree, t_id, str(round(temp_now))+"\N{DEGREE SIGN}")
	
