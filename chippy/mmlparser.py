
class MMLParser(object):
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
        self.notes = {"C": 261.63, "C#": 277.183,
                      "D": 293.66, "D#": 311.127,
                      "E": 329.63,
                      "F": 349.23, "F#": 369.994,
                      "G": 392.00, "G#": 415.305,
                      "A": 440.00, "A#": 466.164,
                      "B": 493.88, "R": 0.1}
        self.current_channel = None
        self.channel_a_queue = []
        self.channel_b_queue = []
        self.channel_c_queue = []
        self.channel_d_queue = []
        self.channel_e_queue = []

    def _parse_header(self):
        for line in self.raw_mml_data:
            if line.startswith("#INCLUDE"):
                # TODO: implement this.
                pass
            elif line.startswith("#TITLE"):
                self.mml_title = line[7:]
            elif line.startswith("#COMPOSER"):
                self.mml_composer = line[10:]
            elif line.startswith("#PROGRAMER"):
                self.mml_programmer = line[11:]
            elif line.startswith("#PROGRAMMER"):
                self.mml_programmer = line[11:]
            elif line.startswith("#OCTAVE-REV"):
                self.reverse_octave = True

    def _set_channel(self, line):
        # TODO: figure out a better way to set a default channel
        if line.startswith("#"):
            return
        elif line.startswith("A "):
            self.current_channel = self.channel_a_queue
        elif line.startswith("B "):
            self.current_channel = self.channel_b_queue
        elif line.startswith("C "):
            self.current_channel = self.channel_c_queue
        elif line.startswith("D "):
            self.current_channel = self.channel_d_queue
        elif line.startswith("E "):
            self.current_channel = self.channel_e_queue
        else:
            self.current_channel = self.channel_a_queue

    def load_file(self, file_name):
        with open(file_name) as f:
            for line in f.readlines():
                self.raw_mml_data.append(line.strip())
        self._parse_header()

    def parse_line(self, line):
        self._set_channel(line)
        for character in line:
            if character.upper() in self.notes.keys():
                freq = self.notes[character.upper()]
                leng = 60 / self.tempo
                self.current_channel.append((leng, freq))

        # parse line:
        #   - set channel if specified, or skip.
        #   For each character:
        #       skip tempo and macro definitions
        #       queue tuple on the proper channel, containing (note, tempo, octave, length, volume)
        #

        # [self._set_channel(line) for line in self.raw_mml_data]
