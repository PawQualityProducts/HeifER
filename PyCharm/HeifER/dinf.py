# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_box
from .box import read_int
from .box import read_string


class DataInformationBox(Box):
    box_type = 'dinf'
    is_mandatry = True
    quantity = Quantity.EXACTLY_ONE


class DataReferenceBox(FullBox):
    box_type = 'dref'
    is_mandatry = True
    quantity = Quantity.EXACTLY_ONE

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.data_entry = []

    def read(self, file, depth):
        self.depth = depth
        entry_count = read_int(file, 4)
        for _ in range(entry_count):
            box = read_box(file, depth)
            if not box:
                break
            self.data_entry.append(box)

    def writeText(self, file, depth=0):
        super().writeText(file,depth)
        pad = " " * depth
        file.write(" {0}Entries={1}\n".format(pad, len(self.data_entry)))
        for entry in self.data_entry:
            entry.writeText(file,depth+2)


class DataEntryUrlBox(FullBox):
    box_type = 'url '
    is_mandatry = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.location = None

    def read(self, file, depth):
        self.depth = depth
        self.location = read_string(file)

    def writeText(self, file, depth=0):
        super().writeText(file,depth)
        pad = " " * depth
        file.write("{0} Location={1}\n".format(pad, self.location))


class DataEntryUrnBox(FullBox):
    box_type = 'urn '
    is_mandatry = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.name = None
        self.startByte = None

    def read(self, file, depth):
        self.depth = depth
        self.name = read_string(file)
        self.location = read_string(file)

    def writeText(self, file, depth=0):
        super().writeText(file,depth)
        pad = " " * depth
        file.write(" {0} Name={1}\n".format(pad, self.name))
        file.write(" {0} Location={1}\n".format(pad, self.location))