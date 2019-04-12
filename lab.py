from math import pi, sin


def sine_gen(framerate=44100, frequency=440):
    step = 2 * pi * frequency / framerate
    increment = 0
    while True:
        yield sin(step * increment)
        increment += 1


def fm_gen(framerate=44100, carrier=440, modulator=440, mod_amplitude=1.0):
    # FM equation:  sin((2 * pi * carrier) + sin(2 * pi * modulator))
    carrier_step = 2 * pi * carrier / framerate
    modulator_step = 2 * pi * modulator / framerate
    mod_index = mod_amplitude
    increment = 0
    while True:
        yield sin(carrier_step * increment + sin(modulator_step * increment))
        increment += 1


def composite_generator(*generators):
    return (sum(samples) / len(samples) for samples in zip(*generators))
