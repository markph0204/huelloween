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

import pyaudio  # from http://people.csail.mit.edu/hubert/pyaudio/
from phue import Bridge, PhueRegistrationException, Light

logger = logging.getLogger('huestorm')
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
    :param bridge:
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
    chunk = 2048  # Change if too fast/slow, never less than 1024
    scale = 50  # Change if too dim/bright
    exponent = 6  # Change if too little/too much difference between loud and quiet sounds

    bridge.set_light(light.light_id, {'on': True, 'bri': 100, 'transitiontime': 0})

    wf = wave.open(sound_file, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(chunk)

    try:
        while data != '':
            stream.write(data)

            rms = audioop.rms(data, 2)
            level = min(rms / (2.0 ** 16) * scale, 1.0)
            level = level ** exponent
            level = int(level * 255)

            bright = level if (level > 0 and level <= 255) else 1
            ttime = 4

            bridge.set_light(light.light_id,
                             {'bri': bright, 'transitiontime': ttime, 'sat': random.randint(0, 128)})

            # read in the next chunk of data
            data = wf.readframes(chunk)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-audio-devices', help='List audio devices',
                        dest='print_audio_devices', action='store_true')
    parser.add_argument('--host', help='The Hue Bridge IP',
                        default=None)
    parser.add_argument('--light-name', help='Name of a single light',
                        default=None)
    parser.add_argument('--audio-device', help='Specify the audio device (mic) to listen to',
                        type=int, default=0)
    parser.add_argument('--play', help='Play a wav sound with visual light effects')

    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)

    # setup the bridge and light if specified
    if not args.host is None:
        bridge = hue_bridge_init(args.host)
    assert bridge is not None

    if not args.light_name is None:
        light = find_light_by_name(args.light_name, bridge)

    # start
    if args.print_audio_devices:
        print_audio_devices()
        exit(0)
    elif args.play is not None:
        hued_wav_file(args.play, bridge, light)
        exit(0)
    elif not args.host or not args.light_name or args.audio_device == 0:
        parser.exit("--host, --light-name and --audio-device are required.")
    else:
        if not light:
            raise Exception("Light name not found")
        hued_mic_input(args.audio_device, bridge, light)
