# -*- coding: utf-8 -*-
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int

class SampleToChunkBox(FullBox):
    box_type = 'stsc'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize)
        self.entries = []

    def read(self, file, depth):
        entry_count = read_int(file, 4)
        for _ in range(entry_count):
            entry = {}
            entry['first_chunk'] = read_int(file, 4)
            entry['samples_per_chunk'] = read_int(file, 4)
            entry['sample_description_index'] = read_int(file, 4)
            self.entries.append(entry)