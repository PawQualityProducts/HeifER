# -*- coding: utf-8 -*-
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int


class ChunkOffsetBox(FullBox):
    box_type = 'stco'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize, location):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, location=location)
        self.entries = []

    def read(self, file, depth):
        entry_count = read_int(file, 4)

        for _ in range(entry_count):
            entry = {}
            entry['chunk_offset'] = read_int(file, 4)
            self.entries.append(entry)