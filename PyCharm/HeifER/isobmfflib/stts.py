
# -*- coding: utf-8 -*-
from .box import FullBox
from .box import read_int

class TimeToSampleBox(FullBox):
    box_type = 'stts'
    is_mandatory = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, startByte=startByte)
        self.entry_count = None
        self.entries = []

    def read(self, file, depth):
        self.depth = depth
        self.entry_count = read_int(file, 4)
        for _ in range(self.entry_count):
            entry = {}
            entry['sample_count'] = read_int(file, 4)
            entry['sample_delta'] = read_int(file, 4)
            self.entries.append(entry)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} entries={1}\n".format(pad, len(self.entries)))
        for entry in self.entries:
            file.write("{0}   sample_count={1}\n".format(pad, entry['sample_count']))
            file.write("{0}   sample_delta={1}\n".format(pad, entry['sample_delta']))
            
            