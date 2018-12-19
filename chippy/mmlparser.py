import re
import collections


Note = collections.namedtuple("Note", ['frequency', 'length', 'volume'])


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
        self.raw_mml_data = ""

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

        token_specification = [('TITLE',        r"(?:#TITLE (.*))"),
                               ('COMPOSER',     r"(?:#COMPOSER (.*))"),
                               ('PROGRAMMER',   r"(?:#PROGRAM{1,2}ER (.*))"),
                               ('TEMPO',        r"([Tt]+\d{3})"),
                               ('NOTE',         r"([cdefgab]\+?-?\d?)"),
                               ('CHANNEL',      r"([ABCDEFG])"),
                               ('OCTAVEUP',     r"(>)"),
                               ('OCTAVEDOWN',   r"(<)"),
                               ('REST',         r"([\.rp])"),
                               ('LENGTH',       r"(l+\d{1,2})")]

        self.token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    def load_from_file(self, file_name):
        """Load a text file containing valid MML."""
        with open(file_name) as f:
            self.raw_mml_data = f.read()

    def load_from_string(self, string):
        """Load a string containing MML data."""
        self.raw_mml_data = string

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

    def parse_mml(self):

        for mo in re.finditer(self.token_regex, self.raw_mml_data):

            kind = mo.lastgroup
            value = mo.group()

            if kind == 'TITLE':
                self.mml_title = value

            print(kind, value)