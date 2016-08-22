import struct
import random
import itertools
from math import *


class Synthesizer:
    def __init__(self, framerate=44100):
        self.framerate = framerate
        self._amplitude_scale = 32767   # Default for 16-bit audio.
        self._channels = 1              # Currently only one channel is supported
        self._bits = 16

    # Generators for various waveforms:

    # def digitar_generator(self, frequency=440, amplitude=0.5, decay=0.996):
    #     period = int(self.framerate / frequency)
    #     amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
    #     ring_buffer = [random.uniform(-1, 1) for _ in range(period)]
    #
    #     for i in range(period):
    #         ring_buffer.append(0.996 * (ring_buffer[0] + ring_buffer[1]) / 2)
    #         ring_buffer.pop(0)
    #
    #     lookup_table = [ring_buffer[0] * amplitude]

    def fm_generator(self, carrier=440, modulator=440, amplitude=0.5, mod_amplitude=1.0):
        period = int(self.framerate / carrier)
        amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
        car_step = 2 * pi * carrier
        mod_step = 2 * pi * modulator
        lookup_table = [(sin(car_step * (i / self.framerate) +
                             mod_amplitude * sin(mod_step * (i / self.framerate)))
                         * amplitude) for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def sine_generator(self, frequency=440.0, amplitude=0.5):
        period = int(self.framerate / frequency)
        amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
        lookup_table = [amplitude * sin(2 * pi * frequency * (i % period / self.framerate))
                        for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def triangle_generator(self, frequency=440.0, amplitude=0.5):
        period = int(self.framerate / frequency)
        amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
        half_period = period / 2
        lookup_table = [(amplitude / half_period) *
                        (half_period - abs(i % period - half_period) * 2 - 1)
                        for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def sawtooth_generator(self, frequency=440.0, amplitude=0.5):
        period = int(self.framerate / frequency)
        amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
        lookup_table = [amplitude * (frequency * (i % period / self.framerate) * 2 - 1)
                        for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def pulse_generator(self, frequency=440.0, amplitude=0.5, duty_cycle=50):
        period = int(self.framerate / frequency)
        amplitude = 0 if amplitude < 0 else 1 if amplitude > 1 else amplitude
        duty_cycle = int(duty_cycle * period / 100)
        lookup_table = [amplitude * (int(i < duty_cycle) * 2 - 1) for i in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    def noise_generator(self, frequency=440.0, amplitude=0.5):
        period = int(self.framerate / frequency)
        lookup_table = [amplitude * (random.uniform(-1, 1)) for _ in range(period)]
        return (lookup_table[i % period] for i in itertools.count(0))

    @staticmethod
    def composite_generator(*generators):
        """Creates a composited generator of all input generators.

        :param generators: Two or more wave generators.
        :return: A new generator with the summed value of the input generators.
        """
        return (sum(samples) / len(samples) for samples in zip(*generators))

    # The following function packs lists of numeric representation into raw bytes:

    def pack_pcm_data(self, wave_generator, length):
        samples = []
        [samples.append(int(self._amplitude_scale * next(wave_generator)))
         for _ in range(int(self.framerate * length))]
        # pack X number of shorts ("_h") into a raw byte string.
        return struct.pack(str(len(samples)) + 'h', *samples)

    # Return raw PCM data (no wave header):

    def fm_pcm(self, length=1.0, **kwargs):
        fm_gen = self.fm_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=fm_gen, length=length)

    def sine_pcm(self, length=1.0, **kwargs):
        wave_gen = self.sine_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def triangle_pcm(self, length=1.0, **kwargs):
        wave_gen = self.triangle_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def saw_pcm(self, length=1.0, **kwargs):
        wave_gen = self.sawtooth_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def pulse_pcm(self, length=1.0, **kwargs):
        wave_gen = self.pulse_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

    def noise_pcm(self, length=1.0, **kwargs):
        wave_gen = self.noise_generator(**kwargs)
        return self.pack_pcm_data(wave_generator=wave_gen, length=length)

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

    # Return RIFF wave data

    def fm_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.fm_pcm(length, **kwargs))

    def sine_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.sine_pcm(length, **kwargs))

    def triangle_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.triangle_pcm(length, **kwargs))

    def saw_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.saw_pcm(length, **kwargs))

    def pulse_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.pulse_pcm(length, **kwargs))

    def noise_riff(self, length=1.0, **kwargs):
        return self.add_wave_header(self.noise_pcm(length, **kwargs))

    # Save wave data to disk

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
