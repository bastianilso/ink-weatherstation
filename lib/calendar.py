#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import caldav
from lxml import etree
from datetime import date, timedelta

caldav_url = ''
username = ''
user_pw = ''

with open('auth.json', 'r') as json_file:
    data = json.loads(json_file.read())
    caldav_url = data['url']
    username = data['user']
    user_pw  = data['pw']

client = caldav.DAVClient(url=caldav_url, username=username, password=user_pw)

def FetchTodaysProgram(calendars):
    cal = calendars[0]
    for c in calendars:
        print(c.name)
        if c.name == "SandraBastianKalender":
            cal = c
    events_fetched = cal.date_search(start=date.today(), end=date.today() + timedelta(days=1), expand=True)
    for e in events_fetched:
        print(e.vobject_instance.vevent.summary.value)
    e_val = [" " for i in range(6)]

    for i in range(len(events_fetched)):
        print(events_fetched[i].vobject_instance.vevent.summary.value)
        e_val[i] = events_fetched[i].vobject_instance.vevent.summary.value

    if len(events_fetched) == 0:
        e_val[0] = "ingen planer."
    return(e_val)

def FetchMonthBirthdays(calendars):
    cal = calendars[0]
    for c in calendars:
        if c.name == "Contact birthdays":
            cal = c
    events_fetched = cal.date_search(start=date.today().replace(day=1), end=date.today().replace(day=1) + timedelta(days=31), expand=True)
    for e in events_fetched:
        print(e.vobject_instance.vevent.summary.value)
    bd_val = [" " for i in range(6)]
    bn_val = [" " for i in range(6)]

    for i in range(len(events_fetched)):
        bd_val[i] = events_fetched[i].vobject_instance.vevent.dtstart.value.strftime("%d/%m")
        name = events_fetched[i].vobject_instance.vevent.summary.value[2:]
        bn_val[i] = (name[:24] + '..') if len(name) > 24 else name

    if len(events_fetched) == 0:
        bd_val[0] = "ingen fødselsdage."
    return(bn_val, bd_val)

def SetEvent(tree, identifier, value):
  root = tree.getroot()
  for elem in root.getiterator():
      try:
          elem.text = elem.text.replace(identifier, value)
      except AttributeError:
          pass


def CalendarUpdate(tree):
    my_principal = client.principal()
    calendars = my_principal.calendars()
    
    cal_events = FetchTodaysProgram(calendars)
    for i in range(5):
        print(cal_events[i])
        c_id = "$c" + str(i)
        print(c_id)
        SetEvent(tree, c_id, cal_events[i])

    
    b_names, b_dates = FetchMonthBirthdays(calendars)
    for i in range(5):
        bd_id = "$b" + str(i)
        bn_id = "$bn" + str(i)
        SetEvent(tree, bd_id, b_dates[i])
        SetEvent(tree, bn_id, b_names[i])

