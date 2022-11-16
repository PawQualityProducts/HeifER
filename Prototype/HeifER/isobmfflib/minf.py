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
        file.write("{0} graphicsmode={1}\n".format(pad, self.graphicsmode))
        file.write("{0} opcolor={1}\n".format(pad, self.opcolor))


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
        file.write("{0} balance={1}\n".format(pad, self.balance))
        file.write("{0} reserved={1}\n".format(pad, self.reserved))


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
        file.write("{0} max_pdu={1}\n".format(pad, self.max_pdu))
        file.write("{0} avg_pdu_size={1}\n".format(pad, self.avg_pdu_size))
        file.write("{0} max_bit_rate={1}\n".format(pad, self.max_bit_rate))
        file.write("{0} avg_bit_rate={1}\n".format(pad, self.avg_bit_rate))
        file.write("{0} reserved={1}\n".format(pad, self.reserved))


class NullMediaHeaderBox(FullBox):
    box_type = 'nmhd'
    is_mandatory = True
