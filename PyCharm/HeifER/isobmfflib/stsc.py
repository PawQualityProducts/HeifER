# -*- coding: utf-8 -*-
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int

class SampleToChunkBox(FullBox):
    box_type = 'stsc'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.entries = []

    def read(self, file, depth):
        self.depth = depth
        entry_count = read_int(file, 4)
        for _ in range(entry_count):
            entry = {}
            entry['first_chunk'] = read_int(file, 4)
            entry['samples_per_chunk'] = read_int(file, 4)
            entry['sample_description_index'] = read_int(file, 4)
            self.entries.append(entry)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} entries={1}\n".format(pad, len(self.entries)))
        for entry in self.entries:
            file.write("{0}   first_chunk={1}\n".format(pad, entry['first_chunk']))
            file.write("{0}   samples_per_chunk={1}\n".format(pad, entry['samples_per_chunk']))
            file.write("{0}   sample_description_index={1}\n".format(pad, entry['sample_description_index']))
            
