# -*- coding: utf-8 -*-
from .box import Box
from .box import FullBox
from .box import Quantity
from .box import read_int


class MediaInformationBox(Box):
    box_type = 'minf'
    is_mandatory = True
    quantity = Quantity.EXACTLY_ONE


class VideoMediaHeaderBox(FullBox):
    box_type = 'vmhd'
    is_mandatory = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.graphicsmode = None
        self.opcolor = []

    def read(self, file, depth):
        self.depth = depth
        self.graphicsmode = read_int(file, 2)
        for _ in range(3):
            self.opcolor.append(read_int(file, 2))

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


class SoundMediaHeaderBox(FullBox):
    box_type = 'smhd'
    is_mandatory = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.balance = None
        self.reserved = None

    def read(self, file, depth):
        self.depth = depth
        self.balance = read_int(file, 2)
        self.reserved = read_int(file, 2)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


class HintMediaHeaderBox(FullBox):
    box_type = 'hmhd'
    is_mandatory = True

    def __init__(self, size, version, flags, largesize, startByte):
        super().__init__(size=size, version=version, flags=flags, largesize=largesize, startByte=startByte)
        self.max_pdu_size = None
        self.avg_pdu_size = None
        self.max_bit_rate = None
        self.avg_bit_rate = None
        self.reserved = None

    def read(self, file, depth):
        self.depth = depth
        self.max_pdu_size = read_int(file, 2)
        self.avg_pdu_size = read_int(file, 2)
        self.max_bit_rate = read_int(file, 4)
        self.avg_bit_rate = read_int(file, 4)
        self.reserved = read_int(file, 4)

    def writeText(self, file, depth=0):
        super().writeText(file, depth)
        pad = " " * depth
        file.write("{0} TODO: Implement writeText for {1}\n".format(pad, self.box_type))


class NullMediaHeaderBox(FullBox):
    box_type = 'nmhd'
    is_mandatory = True
