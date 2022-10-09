
# -*- coding: utf-8 -*-
from .box import FullBox
from .box import read_int


class SyncSampleBox(FullBox):
    box_type = 'stss'
    is_mandatory = False

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.entries = []

    def read(self, file, depth):
        self.depth = depth
        entry_count = read_int(file, 4)
        for _ in range(entry_count):
            entry = {}
            entry['sample_number'] = read_int(file, 4)
            self.entries.append(entry)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} entries={1}\n".format(pad, len(self.entries)))
        for entry in self.entries:
            file.write("{0}   sample_number={1}\n".format(pad, entry['sample_number']))

