
# -*- coding: utf-8 -*-
from .box import FullBox
from .box import read_int


class SampleSizeBox(FullBox):
    box_type = 'stsz'
    is_mandatory = False

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.sample_size = None
        self.entries = []

    def read(self, file, depth):
        self.depth = depth
        self.sample_size = read_int(file, 4)
        sample_count = read_int(file, 4)

        if self.sample_size == 0:
            for _ in range(sample_count):
                entry = {}
                entry['entry_size'] = read_int(file, 4)
                self.entries.append(entry)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))

