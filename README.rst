Chippy
======
**Chippy is a module for creating simple "chiptune" style audio waveforms**

Chippy is a pure Python module for creating various types of basic waveforms,
such as Sine, Triangle, Saw, Square/Pulse, etc. It also does simple FM synthesis.
Under the hood are Python generators for each of these waveforms, which can give
you an endless stream of signed integers representing the waves. There are also
methods that will return a specific length of PCM data, with or without a standard
RIFF header. Use it directly in your application, or save the waveforms to disk.

Chippy is not, however, an audio player. It simply creates the waveforms.

Inspired by Zach Denton's **Wavebender** http://github.com/zacharydenton/wavebender

What's New
----------
**0.1.0** - First release! Everything should work fine, but bug reports or improvement
            suggestions are most welcome. There isn't any documentation yet, but the
            code should be pretty easy to understand.


1) Compatibility
----------------
Chippy is developed for Python 3. It will also work on Pypy3 and, being written in pure
Python, should work on any compliant interpreter. Please let me know if you encounter any
issues.

2) Installation
---------------
No installation is necessary. Chippy is a tiny library with no dependencies. Simply copy
the *chippy* directory into the top level of your project folder, and *import chippy*.

If you prefer, Chippy is also available on PyPI for easy installation via pip.

3) Usage
--------
Several types of waveforms are supported: sine, saw, triange, square, and FM. If you just
want to make a byte string of raw PCM data, you can use the **<waveform>_pcm(length=1)** methods.
There is another set of methods for producing standard RIFF format wave data, ready to play:
**<waveform>_riff(length=1)**. You can save this data to disk with the following methods:
**save_wave(pcm_data, filename)** and **save_raw_pcm(pcm_data, filename)**. Here is a quick
example of usage below.

First, import chippy and create an instance of *chippy.Synthesizer*::

    import chippy
    synth = chippy.Synthesizer(framerate=44100)


Create a some waveforms, and then save them to disk. Whether you have raw pcm, or a RIFF wave,
the *synth.save_wave* and *synth.save_raw_pcm* methods will add or remove the RIFF wave header
as appropriate.::

    sine_wave = synth.sine_pcm(length=2, frequency=220, amplitude=0.8)
    saw_wave = synth.saw_riff(length=1, frequency=440)
    synth.save_wave(sine_wave, "wavefile.wav")
    synth.save_raw_pcm(saw_wave, "sawpcm.raw")


The Square and FM waveforms have a few more options. The FM waveform has carrier and modulator
values instead of just frequency, as you would expect. You can also adjust the modulator amplitude.
The Square/Pulse wave has a duty cycle parameter, which is set as a percentage of 0-100::

    fm_pcm = synth.fm_riff(length=2, carrier=440, modulator=122, amplitude=0.9, mod_amplitude=1.0)
    square_pcm = synth.pulse_riff(length=3, frequency=183, duty_cycle=25)


In addition to the methods above which return bytes of wave data, there are also generators
available that will return infinite streams of wave representation data on a scale of -1.0 and 1.0.
I'll try to add more documentation at some point that covers this, but if you have a use for it you
probably already know what to do. Just make an instance of the generator and pull from it::


    sine_generator = synth.sine_generator(frequency=220, amplitude=0.3)
    next(sine_generator)
    ...
