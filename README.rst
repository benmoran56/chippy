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
example of usage:


    import chippy

    synth = chippy.Synthesizer(framerate=44100)

    # Create a raw PCM Sine wave:
    sine_wave = synth.Sine(length=2, frequency=220)
    # Save it to disk with a RIFF wave header:
    synth.save_wave(sine_wave, "wavefile.wav")

    # Make an FM waveform with RIFF header:
    fm_wave = synth.FM(carrier=440, modulator=220)


MORE DOCUMENTATION TO COME!


