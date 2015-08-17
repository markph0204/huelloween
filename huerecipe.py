#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
phue by <<author>> - <<project name>>
<<url>>

<<license>>

<<description>>
'''

import platform
import time
from ast import literal_eval as make_tuple
from code import InteractiveConsole
import logging

from phue import Bridge, PhueRegistrationException, Light
import random

logger = logging.getLogger('phue')
logging.basicConfig(level=logging.INFO)

__version__ = '0.1'

# light
# color, transition_time, pause
recipe = {"light": 4,
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


def recipe_read(recipe: dict) -> tuple:
    bright, ttime, pause_time = recipe
    if type(bright) is str and bright[0:3] in 'rnd':
        val = make_tuple(bright[3:])
        val = (val[0], val[1]) if (val[0] < val[1]) else (val[1], val[0])
        bright = random.randint(*val)
    return bright, ttime, pause_time


def run_recipe(bridge: Bridge, recipe: dict):
    assert bridge is not None, 'bridge argument passed not valid'
    light = recipe['light']
    sequence = recipe['recipe']
    print(sequence)
    for step in sequence:
        bright, ttime, sleep = recipe_read(step)
        b.set_light(light, {'bri': bright, 'transitiontime': ttime})
        time.sleep(sleep)


def find_light_by_name(name: str, bridge: Bridge) -> Light:
    '''
    Query the bridge finding a matching light by name
    :param name: Name of light to match
    :param bridge:
    :return:
    '''
    for light in bridge.lights:
        if light.name == name:
            logger.debug("Found light: " + light.name)
            blink_light(light, bridge)
            return light
    return None


def blink_light(light: Light, bridge: Bridge):
    '''
    Test turning the light on/off
    :param light:
    :param bridge: The hue bridge
    :return:
    '''
    blink = {'light': light.light_id,
             'recipe': (
                 (255, 1, .2), (0, 1, .1),
                 (255, 0, .2)
             )}
    run_recipe(bridge, blink)
    run_recipe(bridge, blink)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, help='The Hue Bridge IP')
    parser.add_argument('--light-name', required=True, help='Name of a single light')
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)

    while True:
        try:
            b = Bridge(args.host)
            light = find_light_by_name(args.light_name, b)
            if not light:
                raise Exception("Light name not found")
            b.set_light(light.light_id, 'on', True)

            #run_recipe(b, recipe)
            break

        except PhueRegistrationException as e:
            InteractiveConsole().raw_input('Press button on Bridge then hit Enter to try again')
        except Exception as e:
            exit("Failed to run " + e)
