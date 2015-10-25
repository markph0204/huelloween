#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyHueStorm by Mark Hurley - huestorm.py
<<url>>

<<license>>

<<description>>
"""

import argparse
import logging
from code import InteractiveConsole
import audioop
import random
import wave
import time

import yaml
import pyaudio  # from http://people.csail.mit.edu/hubert/pyaudio/
from phue import Bridge, PhueRegistrationException, Light

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

__version__ = '0.1'


def print_audio_devices():
    """
    Print a list of available audio devices (microphones)
    :return:
    """
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(str(i) + '. ' + dev['name'])
        i += 1


def find_light_by_name(name: str, bridge: Bridge) -> Light:
    """
    Query the bridge finding a matching light by name
    :param name: Name of light to match
    :param bridge: The Hue bridge
    :return:
    """
    for light in bridge.lights:
        if light.name == name:
            logger.info("Found light: " + light.name)
            return light
    return None


def hue_bridge_init(host) -> Bridge:
    """
    Initializes the Hue Bridge
    Prompts to press Bridge button if first time
    :param host:
    :return:
    """
    while True:
        try:
            return Bridge(host)
        except PhueRegistrationException as e:
            InteractiveConsole().raw_input('Press button on Bridge then hit Enter to try again')
        except Exception as e:
            exit("Failed to run " + str(e))


def hued_mic_input(input_device: int, bridge: Bridge, light: Light):
    """
    Hue light responds to mic audio input
    :param input_device:
    :param bridge:
    :param light:
    :return:
    """
    chunk = 2048  # Change if too fast/slow, never less than 1024
    scale = 100  # Change if too dim/bright
    exponent = 4  # Change if too little/too much difference between loud and quiet sounds

    # CHANGE THIS TO CORRECT INPUT DEVICE
    # Enable stereo mixing in your sound card
    # to make you sound output an input
    # Use list_devices() to list all your input devices
    device = input_device

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device)

    # b = Bridge('10.0.1.2')
    # b.set_light(4, 'on', False)
    bridge.set_light(light.light_id, {'on': True, 'bri': 100, 'transitiontime': 0})

    print("Starting, use Ctrl+C to stop")
    try:
        last_val = 0
        while True:
            data = stream.read(chunk)
            rms = audioop.rms(data, 2)

            level = min(rms / (2.0 ** 16) * scale, 1.0)
            level = level ** exponent
            level = int(level * 255)
            # print(level)

            bright = level if (level > 0 and level <= 255) else 1
            ttime = 4
            # bright = 128
            # print('{0} | {1}'.format(level, bright))

            if last_val != bright:
                stream.stop_stream()
                bridge.set_light(light.light_id,
                                 {'bri': bright, 'transitiontime': ttime, 'sat': random.randint(0, 128)})
                stream.start_stream()
                last_val = bright

    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping")
        stream.close()
        p.terminate()
        bridge.set_light(4, 'on', False)


def hued_wav_file(sound_file: str, bridge: Bridge, light: Light):
    """
    Hue light responds to WAV sound file
    :param sound_file:
    :param bridge:
    :return:
    """
    chunk = 8192  # Change if too fast/slow, never less than 1024
    scale = 50  # Change if too dim/bright  50
    exponent = 4  # Change if too little/too much difference between loud and quiet sounds

    bridge.set_light(light.light_id,
                     {'on': True, 'bri': 0, 'sat': 1, 'transitiontime': 0})

    wf = wave.open(sound_file, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk)
    old_bright = 0
    try:
        while data != '':
            stream.write(data)

            rms = audioop.rms(data, 2)
            level = min(rms / (2.0 ** 16) * scale, 1.0)
            level = level ** exponent
            level = int(level * 254)
            #print(level)

            bright = level if (level >= 0 and level <= 254) else 0

            diff = abs(old_bright-bright)
            if diff > 50:
                #print("update hue: %s" % diff)
                bridge.set_light(light.light_id, {'bri': bright})

            old_bright = bright

            # read in the next chunk of data
            data = wf.readframes(chunk)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    bridge.set_light(light.light_id,
                     {'on': False, 'bri': 0, 'sat': 0, 'transitiontime': 0})


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-audio-devices', help='List audio devices',
                        dest='print_audio_devices', action='store_true')
    parser.add_argument('--test-mic', action='store_true',
                        help='Test using microphone and one light')
    parser.add_argument('--test-sound', action='store_true',
                        help='Test using audio file and one light')
    args = parser.parse_args()

    if args.print_audio_devices:
        print_audio_devices()
        exit(0)

    config = load_config()
    # print(yaml.dump(config))
    host = config['host']
    sounds = config['sounds']
    lights = config['lights']

    bridge = hue_bridge_init(host)
    assert bridge is not None, "bridge cannot be found"

    if args.test_mic:
        test_config = config['test_mode']
        light = find_light_by_name(test_config['light'], bridge)
        audio_input = test_config['audio_device']
        hued_mic_input(audio_input, bridge, light)
        exit(0)

    if args.test_sound:
        test_config = config['test_mode']
        light = find_light_by_name(test_config['light'], bridge)
        sound_input = test_config['sound']
        hued_wav_file(sound_input, bridge, light)
        exit(0)

    assert host is not None, "no host specified - must configure"
    assert sounds is not None and len(sounds) > 0, "no sounds specified - need at least one"
    assert lights is not None and len(lights) > 0, "no lights specified - need at least one"

    # -------------- NORMAL START ---------------
    RUNNING = True
    while (RUNNING):
        random_light = random.randint(0, len(lights)-1)
        light = find_light_by_name(lights[random_light], bridge)
        random_sound = random.randint(0, len(sounds)-1)
        sound = sounds[random_sound]
        #
        logger.info("Play %s on %s", sound, light)
        hued_wav_file(sound, bridge, light)
        sleep = 10
        logger.info("Sleeping %s secs", sleep)
        time.sleep(sleep)
