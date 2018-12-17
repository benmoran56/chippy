from collections import namedtuple


Note = namedtuple("Note", ['frequency', 'length', 'volume'])



class MMLParser(object):

    notes = {"C": 261.63, "C#": 277.183,
             "D": 293.66, "D#": 311.127,
             "E": 329.63,
             "F": 349.23, "F#": 369.994,
             "G": 392.00, "G#": 415.305,
             "A": 440.00, "A#": 466.164,
             "B": 493.88, "R": 0}

    octave_chart = {0: 0.06,
                    1: 0.12,
                    2: 0.25,
                    3: 0.5,
                    4: 1,
                    5: 2,
                    6: 4,
                    7: 8,
                    8: 16,
                    9: 32,
                    10: 64,
                    11: 128}

    def __init__(self, tempo=120, octave=4, length=4, volume=10):
        self.tempo = tempo              # Tempo scale of 1 to 255
        self.octave = octave            # Octaves from 0 to 7
        self.reverse_octave = False     # Reverses operation of < and >
        self.length = length            # From 1 to 9999
        self.volume = volume            # Volume scale of 0 to 15
        self.raw_mml_data = []
        self.mml_title = None
        self.mml_composer = None
        self.mml_programmer = None

        self.channel_queue = {'a': [],
                              'b': [],
                              'c': [],
                              'd': [],
                              'e': []}

        self.current_channel = 'a'

        self.macros = {}

    def load_from_file(self, file_name):
        """Load a text file containing valid MML."""
        with open(file_name) as f:
            for line in f.readlines():
                self.raw_mml_data.append(line.strip().upper())
        self._parse_header()

    def load_from_string(self, string):
        """Load a string containing MML data."""
        for line in string.splitlines():
            self.raw_mml_data.append(line.strip().upper())
        self._parse_header()

    def _parse_header(self):
        for line in self.raw_mml_data:
            if line.startswith("#INCLUDE"):
                # TODO: implement this.
                pass
            elif line.startswith("#TITLE"):
                self.mml_title = line[6:].strip()
            elif line.startswith("#COMPOSER"):
                self.mml_composer = line[9:].strip()
            elif line.startswith("#PROGRAMER"):
                self.mml_programmer = line[10:].strip()
            elif line.startswith("#PROGRAMMER"):
                self.mml_programmer = line[11:].strip()
            elif line.startswith("#OCTAVE-REV"):
                self.reverse_octave = True

    def _set_channel(self, line):
        if line.startswith("#"):
            return
        elif line.startswith("A "):
            self.current_channel = 'a'
        elif line.startswith("B "):
            self.current_channel = 'b'
        elif line.startswith("C "):
            self.current_channel = 'c'
        elif line.startswith("D "):
            self.current_channel = 'd'
        elif line.startswith("E "):
            self.current_channel = 'e'
        else:
            self.current_channel = 'a'

    def _parse_line(self, line):
        self._set_channel(line)
        for character in line:
            if character == "<":
                self.octave -= 1
            elif character == ">":
                self.octave += 1

            elif character in self.notes.keys():
                freq = self.notes[character] * self.octave_chart[self.octave]
                leng = 60 / self.tempo
                note = Note(frequency=freq, length=leng, volume=self.volume)
                self.channel_queue[self.current_channel].append(note)
        self.octave = 4

    def parse_mml(self):
        for line in self.raw_mml_data:
            self._parse_line(line)
