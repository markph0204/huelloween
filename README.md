# Huelloween

Huelloween processes an audio stream (microphone, wav recording) and adjusts Phillips Hue lights for that scary Halloween effect! It analyzes the amplitude of each frequency using the [Fast Fourier Transform] (https://en.wikipedia.org/wiki/Fast_Fourier_transform) (or FFT) algorithm.


## CONFIG

Edit the ```config.yaml``` file, setting your Phillips Hue bridge IP address.


## Sample Uses

Run Huelloween accepting the mic as the audio input.

Test using the microphone for audio input; first get the audio devices and set in config file

~~~bash
python huelloween.py --list-audio-devices
python huelloween.py --test-mic
~~~

Test using a sample file as input

~~~bash
python huelloween.py --test-sound
~~~

Run normally

~~~bash
python huelloween.py
~~~


The first time you run - you may get prompted to "pair" your program or machine with the Phillips Hue Bridge.  For example:

```
Press button on Bridge then hit Enter to try again
Attempting to set up your Phillips Hue Bridge
INFO:phue:Error opening config file, will attempt bridge registration
INFO:phue:Writing configuration file to /Users/mark/.python_hue
INFO:phue:Reconnecting to the bridge
INFO:phue:Attempting to connect to the bridge...
INFO:phue:Using ip: 10.0.1.2
```


## Dependencies

* Python 3.4/3.6
* [Phue](https://pypi.python.org/pypi/phue/)
* [PyAudio](https://pypi.python.org/pypi/PyAudio)


### MAC OS X (homebrew)

In order to get PyAudio working I had to first install pyaudio C lib.  I used Macports:

```
brew install portaudio
```

### Linux

```
sudo port install portaudio
```


## Mentions

* [Phue](https://github.com/studioimaginaire/phue) Philips Hue Python Library providing a simple, effective and up to date library.

* [Juliana Pena for your helpful article](http://julip.co/2012/05/arduino-python-soundlight-spectrum/) showing just how to process audio in Python and applying the FFT properly!

* Sounds taken from [SoundBible](http://soundbible.com)


## Author

[Mark Hurley](https://github.com/markph0204)


### Backstory

The purpose of Huelloween started just before Halloween 2014.  I wanted to mimic the audio processing of scary recordings to adjust my Phillips Hue lightbulbs.  Each window on the front side of the house would have a light bulb.  It ended up being five windows in all with a speaker sitting just outside in a dark spot.  Some children were scared, parents loved it, while I am sure my neighbors were happy to see it up for only one night.
