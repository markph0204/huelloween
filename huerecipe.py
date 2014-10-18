#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
phue by <<author>> - <<project name>>
<<url>>

<<license>>

<<description>>
'''

import platform
import sys
from phue import Bridge
import time
import random
from ast import literal_eval as make_tuple
if sys.version_info[0] > 2:
    PY3K = True
else:
    PY3K = False

if PY3K:
    import http.client as httplib
else:
    import httplib

import logging
logger = logging.getLogger('phue')
logging.basicConfig(level=logging.INFO)

if platform.system() == 'Windows':
    USER_HOME = 'USERPROFILE'
else:
    USER_HOME = 'HOME'

__version__ = '0.7'

#light
#color, transition_time, pause
recipe = {"light": 2,
        "recipe": (
            ('rnd(100,254)', 1, .1), ('rnd(1, 10)', 0, .3),
            (254, 1, .2), (1, 1, 0),
            ('rnd(100,254)', 1, .5), ('rnd(1, 10)', 0, .3),
            (254, 1, .2), (1, 1, 0),
            ('rnd(100,254)', 1, 1), ('rnd(1, 10)', 0, .3),
            (254, 1, .2), (1, 1, 0),
            ('rnd(100,254)', 1, .1), ('rnd(1, 10)', 0, .3),
            (254, 1, .2), (1, 1, 0),
            (127, 0, 0),
            )}

def recipe_read(recipe):
    bright, ttime, pause_time = recipe
    if type(bright) is str and bright[0:3] in 'rnd':
        val = make_tuple(bright[3:])
        val = (val[0],val[1]) if (val[0] < val[1]) else (val[1],val[0])
        bright = random.randint(*val)
    return bright, ttime, pause_time

def run_recipe(bridge, recipe):
    assert bridge is not None, 'bridge argument passed not valid'
    light = recipe['light']
    sequence = recipe['recipe']
    print (sequence)
    for step in sequence:
        bright, ttime, sleep = recipe_read(step)
        b.set_light(light, {'bri': bright, 'transitiontime': ttime})
        time.sleep(sleep)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)

    while True:
        try:
            b = Bridge(args.host)
            b.set_light(2,'on',True)
            run_recipe(b, recipe)
            break
        except PhueRegistrationException as e:
            raw_input('Press button on Bridge then hit Enter to try again')

