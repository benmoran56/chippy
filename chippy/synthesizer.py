import struct
import random
import itertools

from math import *


class Synthesizer:
    def __init__(self, framerate=44100, amplitude=1.0):
        self.framerate = framerate
        self.amplitude = amplitude
        self._amplitude_scale = 32767   # Default for 16-bit audio.
        self._channels = 1              # Currently only one channel is supported
        self._bits = 16

    def fm_generator(self, carrier=440, modulator=440, mod_amplitude=1.0):
        period = int(self.framerate / carrier)
        car_step = 2 * pi * carrier
        mod_step = 2 * pi * modulator
        lookup_table = [(sin(car_step * (i / self.framerate) +
                             mod_amplitude * sin(mod_step * i / self.framerate)))
                        for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def sine_generator(self, frequency=440.0):
        framerate = self.framerate
        period_length = int(framerate / frequency)
        step = 2 * pi * frequency
        one_period = [sin(step * i / framerate) for i in range(period_length)]
        return itertools.cycle(one_period)

    def triangle_generator(self, frequency=440.0):
        period_length = int(self.framerate / frequency)
        half_period = period_length / 2
        # TODO: fix this really hacky lookup table. The +0.02 is bad. Fix it.
        one_period = [1 / half_period * (half_period - abs(i - half_period) * 2 - 1) + 0.02
                      for i in range(period_length)]
        return itertools.cycle(one_period)

    def sawtooth_generator(self, frequency=440.0):
        period_length = int(self.framerate / frequency)
        one_period = [(frequency * (i / self.framerate) * 2 - 1) for i in range(period_length)]
        return itertools.cycle(one_period)

    def pulse_generator(self, frequency=440.0, duty_cycle=50):
        period_length = int(self.framerate / frequency)
        duty_cycle = int(duty_cycle * period_length / 100)
        one_period = [(int(i < duty_cycle) * 2 - 1) for i in range(period_length)]
        return itertools.cycle(one_period)

    def noise_generator(self, frequency=10.0):
        period = int(self.framerate / frequency)
        lookup_table = [(random.uniform(-1, 1)) for _ in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    @staticmethod
    def silence_generator():
        return itertools.repeat(0)

    @staticmethod
    def composite_generator(*generators):
        """Creates a composited generator of all input generators.

        :param generators: Two or more wave generators.
        :return: A new generator with the summed value of the input generators.
        """
        return (sum(samples) / len(samples) for samples in zip(*generators))

    def adsr_envelope(self, attack, decay, release, length, sustain_level=0.5):
        """An Attack, decay, sustain, release envelope.

        :param attack: The attack rate in seconds.
        :param decay: The decay rate in seconds.
        :param release: The release rate in seconds.
        :param length: The total length in seconds. Must be larger than
        the attack, decay, and release rates combined.
        :param sustain_level: The sustain amplitude, on a scale from 0.0 to 1.0.
        :return: A finite iterator for the length provided.
        """
        assert length >= attack + decay + release
        framerate = int(self.framerate)
        total_bytes = int(framerate * length)
        attack_bytes = int(framerate * attack)
        decay_bytes = int(framerate * decay)
        release_bytes = int(framerate * release)
        sustain_bytes = total_bytes - attack_bytes - decay_bytes - release_bytes

        decay_step = (1 - sustain_level) / decay_bytes
        release_step = sustain_level / release_bytes

        # Attack:
        for i in range(1, attack_bytes + 1):
            yield i / attack_bytes
        # Decay:
        for i in range(1, decay_bytes + 1):
            yield 1 - (i * decay_step)
        # Sustain:
        for i in range(1, sustain_bytes + 1):
            yield sustain_level
        # Release:
        for i in range(1, release_bytes + 1):
            yield sustain_level - (i * release_step)

    def linear_decay_envelope(self, length, peak=1.0):
        """A simple linear decay envelope.

        :param length: The total length in seconds.
        :param peak: The initial peak amplitude, on a scale of 0.0 to 1.0.
        :return: A finite iterator for the length provided.
        """
        total_bytes = int(self.framerate * length)
        for i in range(total_bytes):
            yield (total_bytes - i) / total_bytes * peak

    @staticmethod
    def flat_envelope(amplitude):
        """A flat envelope, which has essentially no effect.

        :param amplitude: The flat amplitude to return.
        :return: An infinite repeat of the amplitude provided.
        """
        return itertools.repeat(amplitude)

    ##############################################################################
    # The following functions pack lists of numeric representation into raw bytes:
    ##############################################################################

    def pack_pcm_data(self, wave_generator, length, envelope=None):
        # Return a bytestring containing the raw waveform data.
        fast_int = int
        amplitude_scale = self._amplitude_scale
        num_bytes = fast_int(self.framerate * length)
        if not envelope:
            envelope = self.flat_envelope(self.amplitude)
        # TODO: rewrite the envelope multiplication so that it's efficent.
        wave_slices = itertools.islice(wave_generator, num_bytes)
        waves = [fast_int(next(envelope) * elem * amplitude_scale) for elem in wave_slices]
        data_format = "<{}h".format(num_bytes)
        return struct.pack(data_format, *waves)

    #######################################
    # Return raw PCM data (no wave header):
    #######################################

    def fm_pcm(self, length=1.0, **kwargs):
        gen = self.fm_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=gen, length=length)

    def fm_pcm_adsr(self, length=1.0, attack=0.05, decay=0.1, release=0.3, sustain=0.5, **kwargs):
        adsr_iterator = self.adsr_envelope(attack, decay, release, length, sustain_level=sustain)
        fm_gen = self.fm_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=fm_gen, length=length, envelope=adsr_iterator)

    def sine_pcm(self, length=1.0, **kwargs):
        wave_gen = self.sine_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def sine_pcm_adsr(self, length=1.0, attack=0.05, decay=0.1, release=0.3, sustain=0.5, **kwargs):
        adsr_iterator = self.adsr_envelope(attack, decay, release, length, sustain_level=sustain)
        gen = self.sine_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=gen, length=length, envelope=adsr_iterator)

    def triangle_pcm(self, length=1.0, **kwargs):
        wave_gen = self.triangle_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def triangle_pcm_adsr(self, length=1.0, attack=0.05, decay=0.1, release=0.3, sustain=0.5, **kwargs):
        adsr_iterator = self.adsr_envelope(attack, decay, release, length, sustain_level=sustain)
        gen = self.triangle_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=gen, length=length, envelope=adsr_iterator)

    def saw_pcm(self, length=1.0, **kwargs):
        wave_gen = self.sawtooth_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def saw_pcm_adsr(self, length=1.0, attack=0.05, decay=0.1, release=0.3, sustain=0.5, **kwargs):
        adsr_iterator = self.adsr_envelope(attack, decay, release, length, sustain_level=sustain)
        gen = self.sawtooth_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=gen, length=length, envelope=adsr_iterator)

    def pulse_pcm(self, length=1.0, **kwargs):
        wave_gen = self.pulse_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def pulse_pcm_adsr(self, length=1.0, attack=0.05, decay=0.1, release=0.3, sustain=0.5, **kwargs):
        adsr_iterator = self.adsr_envelope(attack, decay, release, length, sustain_level=sustain)
        gen = self.pulse_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=gen, length=length, envelope=adsr_iterator)

    def noise_pcm(self, length=1.0, **kwargs):
        wave_gen = self.noise_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    ############################
    # Add a standard RIFF header
    ############################

    def add_wave_header(self, pcm_data):
        """Add a RIFF standard Wave header to raw PCM data

        :param pcm_data: A bytestring of raw PCM data.
        :return: A fully formed Wave object with correct file header,
                 ready to be saved to disk or used directly.
        """
        header = struct.pack('<4sI8sIHHIIHH4sI',
                             b"RIFF",
                             len(pcm_data) + 44 - 8,
                             b"WAVEfmt ",
                             16,                # Default for PCM
                             1,                 # Default for PCM
                             self._channels,
                             self.framerate,
                             self.framerate * self._channels * self._bits // 8,
                             self._channels * self._bits // 8,
                             self._bits,
                             b"data",
                             len(pcm_data))
        return header + pcm_data

    ########################
    # Save wave data to disk
    ########################

    @staticmethod
    def save_raw_pcm(pcm_data, file_name="rawpcm.wav"):
        """Save raw PCM data to disk, removing RIFF header if any.

        :param pcm_data: A bytestring of raw PCM data.
        :param file_name: Desired file name. Defaults to "rawpcm.wav".
        """
        with open(file_name, "wb") as f:
            if bytes(pcm_data[:4]) == b"RIFF":
                f.write(pcm_data[44:])
            else:
                f.write(pcm_data)
            print("saved file: {}".format(file_name))

    def save_wave(self, pcm_data, file_name="riffwave.wav"):
        """Add a RIFF Wave header to raw PCM data, and save to disk.

        :param pcm_data: A bytestring of raw PCM data.
        :param file_name: Desired file name. Defaults to "riffwave.wav".
        """
        with open(file_name, "wb") as f:
            if bytes(pcm_data[:4]) == b"RIFF":
                f.write(pcm_data)
            else:
                f.write(self.add_wave_header(pcm_data))
            print("saved file: {}".format(file_name))
